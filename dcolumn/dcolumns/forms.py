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
from django.utils import six
from django.utils.translation import ugettext, ugettext_lazy as _

from .manager import dcolumn_manager
from .models import CollectionBase, DynamicColumn, ColumnCollection, KeyValue

log = logging.getLogger('dcolumns.dcolumns.forms')


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
        choices = dcolumn_manager.get_related_object_names()
        self.choice_map = dict(choices)
        self.fields['related_model'] = forms.ChoiceField(choices=choices)
        self.fields['related_model'].required = True

    def clean_related_model(self):
        related_model = self.cleaned_data.get('related_model')

        if not related_model or related_model not in self.choice_map:
            raise forms.ValidationError(_("Must choose a related model."))

        return related_model

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
# CollectionBaseFormMixin
#
class CollectionBaseFormMixin(forms.ModelForm):
    """
    This mixin must be used by all forms who's model inherits
    ``CollectionBase``.
    """
    MAX_FIELD_LENGTH_MAP = {
        DynamicColumn.BOOLEAN: 20,
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
        exclude = ['creator', 'updater', 'created', 'updated',]

    def __init__(self, *args, **kwargs):
        """
        The constructor sets up the proper field HTML object.
        """
        super(CollectionBaseFormMixin, self).__init__(*args, **kwargs)
        self.coll_name = ''
        self.relations = {}
        self.fields['column_collection'].required = False
        log.debug("args: %s, kwargs: %s", args, kwargs)
        log.debug("fields: %s, data: %s", self.fields, self.data)

    def clean_column_collection(self):
        """
        Return the ``ColumnCollection`` object for the current collection name.

        :rtype: Django model ``ColumnCollection`` object.
        :raises DoesNotExist: If the record does not exist.
        :raises MultipleObjectsReturned: If multiple objects were returned.
        """
        obj = None

        try:
            self.coll_name = dcolumn_manager.get_collection_name(
                self.Meta.model.__name__)
        except ValueError as e:
            self.add_error(None, str(e))
        else:
            try:
                obj = ColumnCollection.objects.active().get(
                    related_model=self.coll_name)
            except ColumnCollection.DoesNotExist as e:
                msg = _("A ColumnCollection needs to exist before creating "
                        "this object, found collection name {}.").format(
                    self.coll_name)
                log.critical("%s, %s", ugettext(msg), e)
                self.add_error(None, msg)

        return obj

    def clean(self):
        """
        Run validation on models that inherit ``CollectionBase``.

        :rtype: The Django ``cleaned_data`` dict.
        """
        cleaned_data = super(CollectionBaseFormMixin, self).clean()
        request = self.initial.get('request')

        if not request.user.is_authenticated():
            msg = _("You must login to use the site.")
            self.add_error(None, msg)

        try:
            self.relations = ColumnCollection.objects.serialize_columns(
                self.coll_name)
        except Exception as e:
            self.add_error(None, str(e))

        self.validate_dynamic_fields()
        log.debug("Validations errors: %s", self._errors)
        log.debug("cleaned_data: %s", cleaned_data)
        return cleaned_data

    def validate_dynamic_fields(self):
        """
        Validate all validators.
        """
        for relation in self.relations.values():
            log.debug("relation: %s", relation)
            key = relation.get('slug')
            value = self.data.get(key, '')
            value = self.validate_choice_relations(relation, key, value)
            value = self.validate_boolean_type(relation, key, value)
            self.validate_date_types(relation, key, value)
            self.validate_required(relation, key, value)
            self.validate_numeric_type(relation, key, value)
            self.validate_value_length(relation, key, value)
            relation['value'] = value

        log.warn("form.errors: %s", self._errors)

    def validate_choice_relations(self, relation, key, value):
        """
        If ``store_relation`` is False then return the value as is (should be
        a PK). If ``store_relation`` is True then look it up in the related
        ``DynamicColumn.CHOICE`` object using the PK then return the actual
        value for eventual storage in the ``KeyValue`` object.

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
                        value = model.objects.get(pk=value)
                    except model.DoesNotExist:
                        msg = _("Could not find record with value '{}'."
                                ).format(value)
                        self._errors[key] = self.error_class([msg])
                elif value == '':
                    pass
                else:
                    msg = _("Invalid value '{}', must be a number."
                            ).format(value)
                    self._errors[key] = self.error_class([msg])

            # A zero would be the "Choose a value" option which we don't want.
            if (isinstance(value, six.string_types) and value.isdigit() and
                int(value) == 0):
                value = ''

        return value

    _boolean_error = _("Invalid value '{}' must be an integer, numeric "
                       "string, true/false, or yes/no.")

    def validate_boolean_type(self, relation, key, value):
        if relation.get('value_type') == DynamicColumn.BOOLEAN:
            if isinstance(value, six.string_types):
                if value.isdigit():
                    result = str(0 if int(value) == 0 else 1)
                elif (value.lower() in CollectionBase.TRUE_FALSE or
                      value.lower() in CollectionBase.YES_NO):
                    pass
                else:
                    self._errors[key] = self.error_class(
                        [self._boolean_error.format(value)])
            else:
                self._errors[key] = self.error_class(
                    [self._boolean_error.format(value)])

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
        if value and relation.get('value_type') in (DynamicColumn.TIME,
                                                    DynamicColumn.DATE,
                                                    DynamicColumn.DATETIME):
            try:
                dt = dateutil.parser.parse(value)
            except ValueError as e:
                msg = _("Invalid date and/or time object '{}', {}."
                        ).format(value, e)
                self._errors[key] = self.error_class([msg])

    def validate_required(self, relation, key, value):
        """
        Validate if a field is required by the ``DynamicColumn`` meta data
        setting.

        :param relation: A single value set from
                         ``ColumnCollection.objects.serialize_columns()``.
        :param key: The tag attribute value from the POST request.
        :param value: The possibly prepossessed value from the POST request
        """
        if relation.get('required', False) and len(value) == 0:
            msg = _("{} field is required.").format(relation.get('name'))
            self._errors[key] = self.error_class([msg])


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
                msg = _("{} field is not a number.").format(
                    relation.get('name'))
                self._errors[key] = self.error_class([msg])

    def validate_value_length(self, relation, key, value):
        """
        Validate the the incoming data does not exceed the maximum lengths.

        :param relation: A single value set from
                         ``ColumnCollection.objects.serialize_columns()``.
        :param key: The tag attribute value from the POST request.
        :param value: The possibly prepossessed value from the POST request
        """
        # If store_relation is True then the storage type is DynamicColumn.TEXT.
        if not relation.get('store_relation', False):
            value_type = relation.get('value_type')
            log.debug("key: %s, value: %s, value_type: %s",
                      key, value, value_type)

            if len(value) > self.MAX_FIELD_LENGTH_MAP.get(value_type):
                msg = _("{} field is too long.").format(relation.get('name'))
                self._errors[key] = self.error_class([msg])

    def save(self, commit=True):
        """
        Saves a record that inherits from ``CollectionBase`` and all the
        ``KeyValue`` objects related to it.

        :param commit: If ``True`` the record is saved else not saved.
        """
        inst = super(CollectionBaseFormMixin, self).save(commit=False)
        request = self.initial.get('request')
        log.debug("request: %s, inst: %s, instance: %s",
                  request, inst, self.instance)

        if request:
            inst.updater = request.user

            # Populate the creator only on new records.
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
        for pk, relation in self.relations.items():
            value = relation.get('value', '')
            slug = relation.get('slug', '')
            log.debug("pk: %s, slug: %s, value: %s", pk, slug, value)

            if slug and value:
                self.instance.set_key_value(slug, value)


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
            coll_name = self.instance.collection.column_collection.related_model
            columns = ColumnCollection.objects.get_column_collection(coll_name)
            self.fields['dynamic_column'].queryset = columns

    class Meta:
        model = KeyValue
        exclude = []
