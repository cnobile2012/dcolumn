# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/forms.py
#

"""
Dynamic Column forms.
"""
__docformat__ = "restructuredtext en"

import logging
import datetime
import dateutil

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from .manager import dcolumn_manager
from .models import DynamicColumn, ColumnCollection, KeyValue

log = logging.getLogger('dcolumns.dcolumns.views')


#
# ColumnCollection
#
class ColumnCollectionForm(forms.ModelForm):
    """
    Used internally to DColumn in the ``ColumnCollectionAdmin`` class.
    """

    def __init__(self, *args, **kwargs):
        """
        The constructor creates the proper queryset for the DynamicColumn
        HTML choices.
        """
        super(ColumnCollectionForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        columns = ColumnCollection.objects.get_column_collection(
            self.instance.name, unassigned=True)
        self.fields['dynamic_column'].queryset = columns

    class Meta:
        model = ColumnCollection
        exclude = []


#
# DynamicColumn
#
class DynamicColumnForm(forms.ModelForm):
    """
    Used internally to DColumn in the ``DynamicColumnAdmin`` class.
    """

    def __init__(self, *args, **kwargs):
        """
        The constructor sets up the proper ``relation`` field HTML object.
        """
        super(DynamicColumnForm, self).__init__(*args, **kwargs)
        self.fields['relation'] = forms.ChoiceField(
            widget=forms.Select, choices=dcolumn_manager.choice_relations)
        self.fields['relation'].required = False

    class Meta:
        model = DynamicColumn
        exclude = []


#
# CollectionFormMixin
#
class CollectionFormMixin(forms.ModelForm):
    """
    This mixin must be used by all forms who's model inherits
    ``CollectionBase``.
    """
    MAX_FIELD_LENGTH_MAP = {
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
        """
        The constructor sets up the proper field HTML object.
        """
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
        """
        Update objects derived from
        ``ColumnCollection.objects.serialize_columns()`` which are now in
        ``self.relations``. Populate the ``KeyValue`` values except where the
        value was set on an update so as not to overwrite it.

        :rtype: A ``dict`` derived from the
                ``ColumnCollection.objects.serialize_columns()`` dict.
        """
        # Be sure we have an instance and it is an update on the instance
        # not a new instance.
        if self.instance and self.instance.pk is not None:
            for pk, value in self.instance.serialize_key_values().items():
                log.debug("pk: %s, value: %s", pk, value)
                relation = self.relations.setdefault(pk, {})
                # We only want to add new data not overwrite data that is
                # already there.
                if 'value' not in relation:
                    relation['value'] = value.encode('utf-8')

        return self.relations

    def clean_column_collection(self):
        """
        Return the ``ColumnCollection`` object for the current collection name.

        :rtype: Django model ``ColumnCollection`` object.
        :raises DoesNotExist: If the record does not exist.
        :raises MultipleObjectsReturned: If multiple objects were returned.
        """
        try:
            obj = ColumnCollection.objects.active().get(name=self.coll_name)
        except ColumnCollection.DoesNotExist as e:
            msg = _("A ColumnCollection needs to exist before creating this "
                    "object, found collection name {}.").format(self.coll_name)
            log.critical("%s, %s", ugettext(msg), e)
            raise forms.ValidationError(msg)

        return obj

    def clean(self):
        """
        Run validation on models that inherit ``CollectionBase``.

        :rtype: The Django ``cleaned_data`` dict.
        """
        cleaned_data = super(CollectionFormMixin, self).clean()
        self.validate_dynamic_fields()
        log.debug("cleaned_data: %s", cleaned_data)
        return cleaned_data

    def validate_dynamic_fields(self):
        """
        Validate all validators.
        """
        for relation in  self.relations.values():
            log.debug("relation: %s", relation)

            for key, value in self.data.items():
                if key == relation.get('slug'):
                    value = value.encode('utf-8')
                    value = self.validate_choice_relations(relation, key, value)
                    value = self.validate_date_types(relation, key, value)
                    relation['value'] = value
                    self.validate_required(relation, key, value)
                    self.validate_numeric_type(relation, key, value)
                    self.validate_value_length(relation, key, value)

        log.warn("form.errors: %s", self._errors)

    def validate_choice_relations(self, relation, key, value):
        """
        If ``store_relation`` is False then return the value as is from the
        ``KeyValue`` object (should be a PK). If ``store_relation`` is True
        then lookup in the ``CHOICE`` object using the PK and return the
        actual value from the ``KeyValue`` object.

        :param relation: A single value set from
                         ``ColumnCollection.objects.serialize_columns()``.
        :param key: The tag attribute value from the POST request.
        :param value: The possibly prepossessed value from the POST request.
        :rtype: The ``str`` value.
        """
        if relation.get('value_type') == DynamicColumn.CHOICE:
            model, field = dcolumn_manager.get_relation_model_field(
                relation.get('relation', ''))

            if relation.get('store_relation', False):
                if value.isdigit():
                    try:
                        value = model.objects.get_value_by_pk(value, field)
                    except Exception:
                        self._errors[key] = self.error_class(
                            [_("Could not find object with '{}'.").format(
                                value)])
                else:
                    self._errors[key] = self.error_class(
                        [_("Invalid value '{}', must be a number.").format(
                            value)])

        return value

    def validate_date_types(self, relation, key, value):
        """
        Validate the time, date, or datetime object.

        :param relation: A single value set from
                         ``ColumnCollection.objects.serialize_columns()``.
        :param key: The tag attribute value from the POST request.
        :param value: The possibly prepossessed value from the POST request
        :rtype: The ``str`` value.
        """
        if relation.get('value_type') in (DynamicColumn.TIME,
                                          DynamicColumn.DATE,
                                          DynamicColumn.DATETIME):
            try:
                dt = dateutil.parser.parse(value)
            except ValueError as e:
                self._errors[key] = self.error_class(
                    [_("Invalid calendar object '{}', {}.").format(value, e)])

        return value

    def validate_required(self, relation, key, value):
        """
        Validate if a field is required by the ``DynamicColumn`` meta data
        setting.

        :param relation: A single value set from
                         ``ColumnCollection.objects.serialize_columns()``.
        :param key: The tag attribute value from the POST request.
        :param value: The possibly prepossessed value from the POST request
        """
        if relation.get('required', False) and value == '':
            self._errors[key] = self.error_class(
                [_("{} field is required.").format(relation.get('name'))])

    def validate_numeric_type(self, relation, key, value):
        """
        Validate that if a number that the value is a number.

        :param relation: A single value set from
                         ``ColumnCollection.objects.serialize_columns()``.
        :param key: The tag attribute value from the POST request.
        :param value: The possibly prepossessed value from the POST request
        """
        if relation.get('value_type') == DynamicColumn.NUMBER:
            if value and not value.isdigit():
                self._errors[key] = self.error_class(
                    [_("{} field is not a number.").format(
                        relation.get('name'))])

    def validate_value_length(self, relation, key, value):
        """
        Validate the the incoming data does not exceed the maximum lengths.

        :param relation: A single value set from
                         ``ColumnCollection.objects.serialize_columns()``.
        :param key: The tag attribute value from the POST request.
        :param value: The possibly prepossessed value from the POST request
        """
        # If store_relation is True then the storage type is DynamicColumn.TEXT.
        if relation.get('store_relation', False):
            value_type = DynamicColumn.TEXT
        else:
            value_type = relation.get('value_type')

        log.debug("key: %s, value: %s", key, value)

        if len(value) > self.MAX_FIELD_LENGTH_MAP.get(value_type):
                self._errors[key] = self.error_class(
                    [_("{} field is too long.").format(relation.get('name'))])

    def save(self, commit=True):
        """
        Saves a record that inherits from ``CollectionBase`` and all the
        ``KeyValue`` objects related to it.

        :param commit: If ``True`` the record is saved else not saved.
        """
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
            self._save_keyvalues()

        return inst

    def _save_keyvalues(self):
        """
        Save all the ``KeyValue`` objects.
        """
        for pk, relation in self.get_display_data().items():
            required = relation.get('required', False)
            value = relation.get('value', '')
            log.debug("pk: %s, slug: %s, value: %s",
                      pk, relation.get('slug'), relation.get('value'))

            try:
                obj, created = self.instance.keyvalues.get_or_create(
                    collection=self.instance, dynamic_column_id=int(pk),
                    defaults={'value': value})
            except self.instance.MultipleObjectsReturned as e:
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
    """
    Form for validating ``KeyValue`` model objects.
    """

    def __init__(self, *args, **kwargs):
        """
        The constructor sets up the proper field HTML object.
        """
        super(KeyValueForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget = forms.TextInput(
            attrs={'size': 50, 'maxlength': 2000})
        log.debug("args: %s, kwargs: %s", args, kwargs)

        if hasattr(self.instance, 'collection'):
            coll_name = self.instance.collection.column_collection.name
            columns = ColumnCollection.objects.get_column_collection(coll_name)
            self.fields['dynamic_column'].queryset = columns

    class Meta:
        model = KeyValue
        exclude = []
