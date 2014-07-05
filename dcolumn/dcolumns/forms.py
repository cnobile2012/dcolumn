#
# dcolumn/dcolumns/forms.py
#

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from .manager import dcolumn_manager
from .models import DynamicColumn, ColumnCollection, KeyValue

log = logging.getLogger('dcolumn.views')


#
# ColumnCollection
#
class ColumnCollectionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ColumnCollectionForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        columns = ColumnCollection.objects.get_column_collection(
            self.instance.name)
        self.fields[u'dynamic_column'].queryset = columns

    class Meta:
        model = ColumnCollection


#
# DynamicColumn
#
class DynamicColumnForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DynamicColumnForm, self).__init__(*args, **kwargs)
        self.fields[u'relation'] = forms.ChoiceField(
            widget=forms.Select, choices=dcolumn_manager.choice_relations)
        self.fields[u'relation'].required = False

    class Meta:
        model = DynamicColumn

    def clean(self):
        cleaned_data = super(DynamicColumnForm, self).clean()
        value_type = cleaned_data.get(u'value_type')
        relation = cleaned_data.get(u'relation', u'0')
        relation = int(relation)
        log.debug("value_type: %s, relation: %s", value_type, relation)

        if value_type == DynamicColumn.CHOICE:
            if not relation:
                self._errors[u'relation'] = self.error_class(
                        [_(u"If the Value Type is a Choice then a relation "
                           u"must be entered.")])
        else:
            cleaned_data[u'relation'] = None

        return cleaned_data


#
# CollectionMixin
#
class CollectionFormMixin(forms.ModelForm):
    SPECIAL_CASE_MAP = {DynamicColumn.BOOLEAN: u'1',
                        DynamicColumn.CHOICE: u'0'}
    MAX_LENGTH_MAP = {DynamicColumn.NUMBER: 20,
                      DynamicColumn.TEXT: 250,
                      DynamicColumn.TEXT_BLOCK: 2000,
                      DynamicColumn.DATE: 20,
                      DynamicColumn.BOOLEAN: 1,
                      DynamicColumn.FLOAT: 305,
                      DynamicColumn.CHOICE: 12}

    class Meta:
        exclude = ('creator', 'user', 'ctime', 'mtime')

    def __init__(self, *args, **kwargs):
        super(CollectionFormMixin, self).__init__(*args, **kwargs)
        self.coll_name = dcolumn_manager.get_collection_name(
            self.Meta.model.__name__)
        self.relations = ColumnCollection.objects.serialize_columns(
            self.coll_name)
        self.fields[u'column_collection'].required = False
        log.debug("args: %s, kwargs: %s", args, kwargs)
        log.debug("fields: %s, data: %s", self.fields, self.data)

    def get_display_data(self):
        if self.instance and self.instance.pk is not None:
            for pk, value in self.instance.serialize_key_value_pairs().items():
                relation = self.relations.setdefault(pk, {})
                # We do not want to overwrite changed data with the old data
                # so we skip over the below equate.
                if u'value' in relation: continue
                relation[u'value'] = value

        return self.relations

    def clean_column_collection(self):
        return ColumnCollection.objects.active().get(name=self.coll_name)

    def clean(self):
        cleaned_data = super(CollectionFormMixin, self).clean()
        self.validate_dynamic_fields()
        log.debug("cleaned_data: %s", cleaned_data)
        return cleaned_data

    def validate_dynamic_fields(self):
        for relation in  self.relations.values():
            log.debug("relation: %s", relation)

            for key, value in self.data.items():
                if key == relation.get(u'slug'):
                    value = self.validate_store_relation(relation, value)
                    value = self.validate_date_types(relation, key, value)
                    relation[u'value'] = value
                    self.validate_required(relation, key, value)
                    self.validate_value_type(relation, key, value)
                    self.validate_value_length(relation, key, value)

        log.debug("form.errors: %s", self._errors)

    def validate_store_relation(self, relation, value):
        """
        If 'store_relation' is False then return the value as is, should be a
        PK. If 'store_relation' is True then lookup in the choices using the
        PK and return the actual value.
        """
        if relation.get(u'store_related', False):
            log.debug("value: %s, relation: %s", value, relation)
            name = DynamicColumn.CHOICE_RELATION_MAP.get(
                relation.get('relation', u''))
            data = DynamicColumn.MODEL_MAP.get(name)

            if len(data) == 2:
                model, field = data
                old_value = value
                value = value.isdigit() and int(value) or 0
                value = [getattr(r, field)
                         for r in model.objects.dynamic_column()
                         if value == r.pk]
                value = len(value) >= 1 and value[0] or old_value
                log.debug("value: %s, field: %s, model: %s",
                          value, field, model)

        return value

    # SHORT TERM FIX will only work with one data format type.
    _MONTHS = {u'january': 1, u'february': 2, u'march': 3, u'april': 4,
               u'may': 5, u'june': 6, u'july': 7, u'august': 8,
               u'september': 9, u'october': 10, u'november': 11,
               u'december': 12}

    def validate_date_types(self, relation, key, value):
        if relation.get(u'value_type') == DynamicColumn.DATE:
            if value:
                day_month, delim, year = value.partition(', ')
                day, delim, month = day_month.partition(' ')
                month = self._MONTHS.get(month.lower(), 0)
                log.debug("year: %s, month: %s, day: %s", year, month, day)

                if not year.isdigit() or not month or not day.isdigit():
                    self._errors[key] = self.error_class(
                        [u"Invalid year, month, or day, found: {}".format(
                            value)])
                else:
                    value = datetime.date(int(year), month, int(day)).strftime(
                        u'%Y-%m-%d')

        return value

    def validate_required(self, relation, key, value):
        if relation.get(u'required', False):
            value_type = relation.get(u'value_type')

            if (not value or value_type in self.SPECIAL_CASE_MAP and
                self.SPECIAL_CASE_MAP.get(value_type) == value):

                self._errors[key] = self.error_class(
                    [u"{} field is required.".format(relation.get(u'name'))])

    def validate_value_type(self, relation, key, value):
        value_type = relation.get(u'value_type')

        if value_type == DynamicColumn.NUMBER:
            if value and not value.isdigit():
                self._errors[key] = self.error_class(
                    [u"{} field is not a number.".format(
                        relation.get(u'name'))])

    def validate_value_length(self, relation, key, value):
        value_type = relation.get(u'value_type')

        if len(value) > self.MAX_LENGTH_MAP.get(value_type):
                self._errors[key] = self.error_class(
                    [u"{} field is too long.".format(relation.get(u'name'))])

    def save(self, commit=True):
        inst = super(CollectionFormMixin, self).save(commit=False)
        request = self.initial.get('request')
        log.debug("request: %s, inst: %s, instance: %s",
                  request, inst, self.instance)

        if request:
            inst.user = request.user
            inst.active = True

            if not hasattr(inst, u'creator') or not inst.creator:
                inst.creator = request.user

        if commit:
            inst.save()
            #self.save_m2m() # If we have any.
            self._save_keyvalue_pairs()

        return inst

    def _save_keyvalue_pairs(self):
        for pk, relation in self.get_display_data().items():
            required = relation.get(u'required', False)
            value = relation.get(u'value', u'')
            log.debug("pk: %s, slug: %s, value: %s",
                      pk, relation.get(u'slug'), relation.get(u'value'))

            if not required and not value:
                continue

            try:
                obj, created = self.instance.keyvalue_pairs.get_or_create(
                    collection=self.instance, dynamic_column_id=int(pk),
                    defaults={u'value': value})
            except self.instance.MultipleObjectsReturned, e:
                log.error("Multiple records found for parent: %s, "
                          "dynamic_column_id: %s", self.instance,
                          dynamic_column_id=cc_id)
                raise e

            if not created:
                obj.value = value
                obj.save()


#
# KeyValue
#
class KeyValueForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(KeyValueForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)

        if hasattr(self.instance, 'collection'):
            coll_name = self.instance.collection.column_collection.name
            columns = ColumnCollection.objects.get_column_collection(coll_name)
            self.fields[u'dynamic_column'].queryset = columns
        else:
            log.debug("instance: %s", self.instance)


    class Meta:
        model = KeyValue
