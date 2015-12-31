# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/forms.py
#

import logging
import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from .manager import dcolumn_manager
from .models import DynamicColumn, ColumnCollection, KeyValue

log = logging.getLogger('dcolumns.dcolumns.views')


#
# ColumnCollection
#
class ColumnCollectionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ColumnCollectionForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.columns = ColumnCollection.objects.get_column_collection(
            self.instance.name, unassigned=True)
        self.fields['dynamic_column'].queryset = self.columns

    class Meta:
        model = ColumnCollection
        exclude = []

    def clean(self):
        if not self.columns:
            msg = ("No objects in the database, please create initial objects "
                   "in the Dynamic Columns model to be used for this "
                   "collection type.")
            log.error(msg)
            raise forms.ValidationError({'dynamic_column': [msg]})

        return self.cleaned_data


#
# DynamicColumn
#
class DynamicColumnForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DynamicColumnForm, self).__init__(*args, **kwargs)
        self.fields['relation'] = forms.ChoiceField(
            widget=forms.Select, choices=dcolumn_manager.choice_relations)
        self.fields['relation'].required = False

    class Meta:
        model = DynamicColumn
        exclude = []

    def clean(self):
        cleaned_data = super(DynamicColumnForm, self).clean()
        value_type = cleaned_data.get('value_type')
        relation = cleaned_data.get('relation', '0')
        relation = int(relation)
        log.debug("value_type: %s, relation: %s", value_type, relation)

        if value_type == DynamicColumn.CHOICE:
            if not relation:
                self._errors['relation'] = self.error_class(
                        [_("If the Value Type is a Choice then a relation "
                           "must be entered.")])
        else:
            cleaned_data['relation'] = None

        return cleaned_data


#
# CollectionFormMixin
#
class CollectionFormMixin(forms.ModelForm):
    SPECIAL_CASE_MAP = {
        DynamicColumn.BOOLEAN: '1',
        DynamicColumn.CHOICE: '0',
        }
    MAX_LENGTH_MAP = {
        DynamicColumn.BOOLEAN: 1,
        DynamicColumn.CHOICE: 12,
        DynamicColumn.DATE: 20,
        DynamicColumn.DATETIME: 20,
        DynamicColumn.FLOAT: 305,
        DynamicColumn.NUMBER: 20,
        DynamicColumn.TEXT: 250,
        DynamicColumn.TEXT_BLOCK: 2000,
        DynamicColumn.TIME: 20,
        }

    class Meta:
        exclude = ['creator', 'updater', 'created', 'updated']

    def __init__(self, *args, **kwargs):
        super(CollectionFormMixin, self).__init__(*args, **kwargs)
        self.coll_name = dcolumn_manager.get_collection_name(
            self.Meta.model.__name__)
        self.relations = ColumnCollection.objects.serialize_columns(
            self.coll_name)
        self.fields['column_collection'].required = False

        if 'created' in self.fields:
            self.fields['created'].required = False

        if 'updated' in self.fields:
            self.fields['updated'].required = False

        log.debug("args: %s, kwargs: %s", args, kwargs)
        log.debug("fields: %s, data: %s", self.fields, self.data)

    def get_display_data(self):
        if self.instance and self.instance.pk is not None:
            for pk, value in self.instance.serialize_key_value_pairs().items():
                log.debug("pk: %s, value: %s", pk, value)
                relation = self.relations.setdefault(pk, {})
                # We only want to add new data not overwrite data that is
                # already there.
                if 'value' not in relation:
                    relation['value'] = value

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
                if key == relation.get('slug'):
                    value = self.validate_store_relation(relation, value)
                    value = self.validate_date_types(relation, key, value)
                    relation['value'] = value
                    self.validate_required(relation, key, value)
                    self.validate_value_type(relation, key, value)
                    self.validate_value_length(relation, key, value)

        log.warn("form.errors: %s", self._errors)

    def validate_store_relation(self, relation, value):
        """
        If 'store_relation' is False then return the value as is, should be a
        PK. If 'store_relation' is True then lookup in the choices using the
        PK and return the actual value.
        """
        if relation.get('store_relation', False):
            log.debug("value: %s, relation: %s", value, relation)
            data = dcolumn_manager.get_relation_model_field(
                relation.get('relation', ''))

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
    _MONTHS = {'january': 1, 'february': 2, 'march': 3, 'april': 4,
               'may': 5, 'june': 6, 'july': 7, 'august': 8,
               'september': 9, 'october': 10, 'november': 11,
               'december': 12}

    def validate_date_types(self, relation, key, value):
        if relation.get('value_type') == DynamicColumn.DATE:
            if value:
                year = month = day = 0
                day_month, delim, year = value.partition(', ')

                if delim:
                    day, delim, month = day_month.partition(' ')
                    month = self._MONTHS.get(month.lower(), 0)
                else:
                    tmp = value.split('-')

                    if len(tmp) == 3:
                        year, month, day = tmp

                log.debug("year: %s, month: %s, day: %s", year, month, day)

                if not year.isdigit() or not month or not day.isdigit():
                    self._errors[key] = self.error_class(
                        ["Invalid year, month, or day, found: {}".format(
                            value)])
                else:
                    value = datetime.date(int(year), int(month),
                                          int(day)).strftime('%Y-%m-%d')

        return value

    def validate_required(self, relation, key, value):
        if relation.get('required', False):
            value_type = relation.get('value_type')

            if (not value or value_type in self.SPECIAL_CASE_MAP and
                self.SPECIAL_CASE_MAP.get(value_type) == value):

                self._errors[key] = self.error_class(
                    ["{} field is required.".format(relation.get('name'))])

    def validate_value_type(self, relation, key, value):
        value_type = relation.get('value_type')

        if value_type == DynamicColumn.NUMBER:
            if value and not value.isdigit():
                self._errors[key] = self.error_class(
                    ["{} field is not a number.".format(
                        relation.get('name'))])

    def validate_value_length(self, relation, key, value):
        value_type = relation.get('value_type')

        # If store_relation is True then the storage type is DynamicColumn.TEXT.
        if relation.get('store_relation', False):
            value_type = DynamicColumn.TEXT

        log.debug("key: %s, value: %s", key, value)

        if len(value) > self.MAX_LENGTH_MAP.get(value_type):
                self._errors[key] = self.error_class(
                    ["{} field is too long.".format(relation.get('name'))])

    def save(self, commit=True):
        inst = super(CollectionFormMixin, self).save(commit=False)
        request = self.initial.get('request')
        log.debug("request: %s, inst: %s, instance: %s",
                  request, inst, self.instance)

        if request:
            inst.updater = request.user

            if not hasattr(inst, 'creator') or not inst.creator:
                inst.creator = request.user
                inst.active = True

        if commit:
            inst.save()
            #self.save_m2m() # If we have any.
            self._save_keyvalue_pairs()

        return inst

    def _save_keyvalue_pairs(self):
        for pk, relation in self.get_display_data().items():
            required = relation.get('required', False)
            value = relation.get('value', '')
            log.debug("pk: %s, slug: %s, value: %s",
                      pk, relation.get('slug'), relation.get('value'))

            try:
                obj, created = self.instance.keyvalue_pairs.get_or_create(
                    collection=self.instance, dynamic_column_id=int(pk),
                    defaults={'value': value})
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
        self.fields['value'].widget = forms.TextInput(
            attrs={'size': 50, 'maxlength': 2000})
        log.debug("args: %s, kwargs: %s", args, kwargs)
        #log.debug("dir(self): %s", dir(self))

        if hasattr(self.instance, 'collection'):
            coll_name = self.instance.collection.column_collection.name
            columns = ColumnCollection.objects.get_column_collection(coll_name)
            self.fields['dynamic_column'].queryset = columns

    class Meta:
        model = KeyValue
        exclude = []
