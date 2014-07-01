#
# dcolumn/dcolumns/forms.py
#

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from .manager import dcolumn_manager
from .models import DynamicColumn, ColumnCollection

log = logging.getLogger('dcolumn.views')


#
# ColumnCollection
#
class ColumnCollectionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ColumnCollectionForm, self).__init__(*args, **kwargs)
        self.fields[
            u'dynamic_column'].queryset = DynamicColumn.objects.active()

    class Meta:
        model = ColumnCollection


#
# DynamicColumn
#
class DynamicColumnForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DynamicColumnForm, self).__init__(*args, **kwargs)
        #self.fields[u'relation'].widget = forms.TypedChoiceField()
        #self.fields[u'relation'].empty_label = _("Choose a relation")
        #self.fields[u'relation'].queryset = dcolumn_manager.choice_relations

    class Meta:
        model = DynamicColumn

    def clean(self):
        cleaned_data = super(DynamicColumnForm, self).clean()
        value_type = cleaned_data.get(u'value_type')
        relation = cleaned_data.get(u'relation')

        if value_type == DynamicColumn.CHOICE:
            if relation is None:
                msg = (u"If the Value Type is a Choice then a relation "
                       u"must be entered.")
                raise forms.ValidationError(msg)
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
        self.relations = ColumnCollection.objects.serialize_columns()
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
        return ColumnCollection.objects.active().get(
            name=dcolumn_manager.get_default_column_name(u'Parent'))

    def clean(self):
        cleaned_data = super(ParentForm, self).clean()
        self.validate_dynamic_fields()
        log.debug("cleaned_data: %s", cleaned_data)
        return cleaned_data

    def validate_dynamic_fields(self):
        error_class = []

        for relation in  self.relations.values():
            log.debug("relation: %s", relation)

            for key, value in self.data.items():
                if key == relation.get(u'slug'):
                    self.validate_store_required(relation, value)
                    relation[u'value'] = value
                    self.validate_required(relation, error_class, key, value)
                    self.validate_value_type(relation, error_class, key, value)
                    self.validate_value_length(relation, error_class, key,
                                               value)

        log.error("form.errors: %s", self._errors)

    def validate_store_required(self, relation, value):
        if relation.get(u'store_related'):
            print value


    def validate_required(self, relation, error_class, key, value):
        if relation.get(u'required', False):
            value_type = relation.get(u'value_type')

            if (not value or value_type in self.SPECIAL_CASE_MAP and
                self.SPECIAL_CASE_MAP.get(value_type) == value):

                self._errors[key] = self.error_class(
                    [u"{} field is required.".format(relation.get(u'name'))])

    def validate_value_type(self, relation, error_class, key, value):
        value_type = relation.get(u'value_type')

        if value_type == DynamicColumn.NUMBER:
            if value and not value.isdigit():
                self._errors[key] = self.error_class(
                    [u"{} field is not a number.".format(
                        relation.get(u'name'))])

    def validate_value_length(self, relation, error_class, key, value):
        value_type = relation.get(u'value_type')

        if len(value) > self.MAX_LENGTH_MAP.get(value_type):
                self._errors[key] = self.error_class(
                    [u"{} field is too long.".format(relation.get(u'name'))])

    def save(self, commit=True):
        inst = super(ParentForm, self).save(commit=False)
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

        # TODO See if the pk can be an int from the beginning.

        for pk, relation in self.get_display_data().items():
            required = relation.get(u'required', False)
            value = relation.get(u'value', u'')
            log.debug("pk: %s, slug: %s, value: %s",
                      pk, relation.get(u'slug'), relation.get(u'value'))

            if not required and not value:
                continue

            try:
                obj, created = self.instance.keyvalue_pairs.get_or_create(
                    parent=self.instance, dynamic_column_id=int(pk),
                    defaults={u'value': value})
            except Parent.MultipleObjectsReturned, e:
                log.error("Multiple records found for parent: %s, "
                          "dynamic_column_id: %s",
                          self.instance, dynamic_column_id=cc_id)
                raise e

            if not created:
                obj.value = value
                obj.save()
