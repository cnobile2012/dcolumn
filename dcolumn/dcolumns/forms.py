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
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from .manager import dcolumn_manager
from .models import CollectionBase, DynamicColumn, ColumnCollection, KeyValue

log = logging.getLogger('dcolumns.dcolumns.forms')


#
# CollectionBaseFormMixin
#
class CollectionBaseFormMixin(forms.ModelForm):
    """
    This mixin must be used by all forms who's model inherits
    ``CollectionBase``.
    """
    column_collection = forms.ModelChoiceField(
        queryset=None, empty_label=None, required=False)

    def __init__(self, *args, **kwargs):
        """
        The constructor sets up the proper field HTML object.
        """
        self.request = kwargs.pop('request', None)
        super(CollectionBaseFormMixin, self).__init__(*args, **kwargs)
        self.coll_name = ''
        self.relations = {}
        log.debug("CollectionBaseFormMixin fields: %s, data: %s",
                  self.fields, self.data)

    def clean_column_collection(self):
        """
        Return the ``ColumnCollection`` object for the current collection
        name.

        :rtype: Django model ``ColumnCollection`` object.
        :raises ColumnCollection.DoesNotExist: If the record does not exist.
                                               This usually means that a
                                               ``ColumnCollection`` has not
                                               been defined in the admin.
        """
        obj = None

        try:
            obj = ColumnCollection.objects.active().get(
                related_model__iexact=self.Meta.model.__name__)
        except ColumnCollection.DoesNotExist as e: # pragma: no cover
            msg = _("A ColumnCollection needs to exist before creating "
                    "this object, found collection name {}."
                    ).format(self.Meta.model.__name__)
            log.critical("%s, %s", msg, e)
            self.add_error('column_collection', msg)

        return obj

    def clean(self):
        """
        Run validation on models that inherit ``CollectionBase``.
        :rtype: The Django ``cleaned_data`` dict.
        """
        cleaned_data = super(CollectionBaseFormMixin, self).clean()
        request = self.initial.get('request')

        try:
            self.relations = ColumnCollection.objects.serialize_columns(
                self.Meta.model.__name__, by_slug=True)
        except Exception as e: # pragma: no cover
            self.add_error(None, str(e))

        log.debug("cleaned_data: %s", cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        """
        Saves a record that inherits from ``CollectionBase`` and all the
        ``KeyValue`` objects related to it.
        :param commit: If ``True`` the record is saved else not saved.
        """
        inst = super(CollectionBaseFormMixin, self).save(commit=False)
        request = self.initial.get('request')
        data = dict(self.cleaned_data)
        error = False

        if request:
            inst.updater = request.user

            # Populate the creator only on new records.
            if not hasattr(inst, 'creator') or not inst.creator:
                inst.creator = request.user
                inst.active = True

        for slug, value in data.items():
            relation = self.relations.get(slug)
            if value is None: continue
            force = False if value != '' else True

            if relation:
                try:
                    inst.set_key_value(slug, value, force=force, defer=True)
                except ValueError as e:
                    error = True

                    if (relation.get('required')
                        or (not relation.get('required') and value)):
                        self.add_error(slug, e)

        log.debug("Validations errors: %s", error)

        if commit and not error:
            inst.save()
            inst.save_deferred()

        return inst

    class Meta:
        fields = ['column_collection',]
        exclude = ['creator', 'updater', 'created', 'updated',]


#
# ColumnCollectionAdminForm
#
class ColumnCollectionAdminForm(forms.ModelForm):
    """
    Used internally to DColumn in the ``ColumnCollectionAdmin`` class.
    """

    def __init__(self, *args, **kwargs):
        """
        The constructor creates the proper queryset for the DynamicColumn
        HTML choices.
        """
        self.request = kwargs.pop('request', None)

        if not self.request:
            initial = kwargs.get('initial', {})
            self.request = initial.get('request')

        super(ColumnCollectionAdminForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        columns = ColumnCollection.objects.get_column_collection(
            self.instance.related_model, unassigned=True)
        self.fields['dynamic_column'].queryset = columns
        choices = dcolumn_manager.get_related_object_names()
        self.choice_map = dict(choices)
        self.fields['related_model'] = forms.ChoiceField(choices=choices)
        self.fields['related_model'].required = True
        log.debug("name: %s, columns: %s",
                  self.instance.related_model, columns)

    def clean_related_model(self):
        related_model = self.cleaned_data.get('related_model')

        if not related_model or related_model not in self.choice_map:
            raise forms.ValidationError(_("Must choose a related model."))

        return related_model

    class Meta:
        model = ColumnCollection
        exclude = []


#
# KeyValueAdminForm
#
class KeyValueAdminForm(forms.ModelForm):
    """
    Form for validating ``KeyValue`` model objects.
    """

    def __init__(self, *args, **kwargs):
        """
        The constructor sets up the proper field HTML object.
        """
        super(KeyValueAdminForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)

        if hasattr(self.instance, 'collection'):
            coll_name = (self.instance.collection.column_collection
                         .related_model)
            columns = ColumnCollection.objects.get_column_collection(coll_name)
            self.fields['dynamic_column'].queryset = columns

    class Meta:
        model = KeyValue
        exclude = []


#
# DynamicColumnAdminForm
#
class DynamicColumnAdminForm(forms.ModelForm):
    """
    Used internally to DColumn in the ``DynamicColumnAdmin`` class.
    """

    def __init__(self, *args, **kwargs):
        """
        The constructor sets up the proper ``relation`` field HTML object.
        """
        self.request = kwargs.pop('request', None)

        if not self.request:
            initial = kwargs.get('initial', {})
            self.request = initial.get('request')

        super(DynamicColumnAdminForm, self).__init__(*args, **kwargs)
        self.fields['location'] = forms.ChoiceField(
            widget=forms.Select, choices=dcolumn_manager.css_containers)
        self.fields['relation'] = forms.ChoiceField(
            widget=forms.Select, choices=dcolumn_manager.choice_relations)
        self.fields['relation'].required = False

    class Meta:
        model = DynamicColumn
        exclude = []
