# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/models.py
#

"""
Dynamic Column dependent models

by: Carl J. Nobile

email: carl.nobile@gmail.com
"""
__docformat__ = "restructuredtext en"

import logging
import datetime
import dateutil
import types
from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin,
    ValidateOnSaveMixin)

from .manager import dcolumn_manager

log = logging.getLogger('dcolumns.dcolumns.models')


#
# DynamicColumn
#
class DynamicColumnManager(StatusModelManagerMixin):
    """
    Supplies methods to the DynamicColumn objects instance.
    """

    def get_fk_slugs(self):
        """
        This method returns a dict of the relation class name and slug.

        :Returns:
          A dict of {<relation class name>: <slug>, ...}
        """
        result = {}

        for record in self.active():
            if record.value_type == self.model.CHOICE:
                name = dcolumn_manager.choice_relation_map.get(record.relation)
                result[name] = record.slug

        return result


class DynamicColumn(TimeModelMixin, UserModelMixin, StatusModelMixin,
                    ValidateOnSaveMixin):
    """
    This model defines all the fields used in models that implement dynamic
    columns.
    """
    BOOLEAN = 1
    CHOICE = 2
    DATE = 3
    DATETIME = 4
    FLOAT = 5
    NUMBER = 6
    TEXT = 7
    TEXT_BLOCK = 8
    TIME = 9
    VALUE_TYPES = (
        (BOOLEAN, _("Boolean")),
        (CHOICE, _("Choice")),
        (DATE, _("Date")),
        (DATETIME, ("Date Time")),
        (FLOAT, _("Floating Point")),
        (NUMBER, _("Number")),
        (TEXT, _("Text")),
        (TEXT_BLOCK, _("Text Block")),
        (TIME, ("Time")),
        )
    VALUE_TYPES_MAP = dict(VALUE_TYPES)
    NO = False
    YES = True
    YES_NO = (
        (NO, _("No")),
        (YES, _("Yes"))
        )

    name = models.CharField(
        verbose_name=_("Name"), max_length=50,
        help_text=_("Enter a column name."))
    preferred_slug = models.SlugField(
        verbose_name=_("Preferred Slug"), null=True, blank=True,
        help_text=_("If you don't want the slug to change when the name "
                    "changes enter a slug here. However, if you change this "
                    "field the slug will track it."))
    slug = models.SlugField(
        verbose_name=_("Slug"), editable=False,
        help_text=_("This field is normally created from the name field, "
                    "however, if you want to prevent it from changing when "
                    "the name changes enter a preferred slug above."))
    value_type = models.IntegerField(
        verbose_name=_("Value Type"), choices=VALUE_TYPES,
        help_text=_("Choose the value type."))
    relation = models.IntegerField(
        verbose_name=_("Choice Relation"), null=True, blank=True,
        help_text=_("Choose the Choice Relation Type."))
    required = models.BooleanField(
        verbose_name=_("Required Field"), choices=YES_NO, default=NO,
        help_text=_("If this field is required based on business rules then "
                    "choose 'Yes'."))
    store_relation = models.BooleanField(
        verbose_name=_("Store Relation Value"), choices=YES_NO, default=NO,
        help_text=_("Store the literal value not the primary key of the "
                    "relation (used when choices change often). The most "
                    "common usage is the default 'No', to not store."))
    location = models.CharField(
        verbose_name=_("Display Location"), max_length=50,
        choices=dcolumn_manager.css_containers,
        help_text=_("Choose a display location."))
    order = models.PositiveSmallIntegerField(verbose_name='Display Order')

    objects = DynamicColumnManager()

    def _relation_producer(self):
        result = ''

        if self.relation is not None:
            result = dcolumn_manager.choice_relation_map.get(self.relation, '')

        return result
    _relation_producer.short_description = _("Relation")

    def _collection_producer(self):
        result = []

        for collection in self.column_collection.all():
            result.append('<span>{}</span>'.format(collection.name))

        return ", ".join(result)
    _collection_producer.short_description = _("Collections")
    _collection_producer.allow_tags = True

    def clean(self):
        if self.preferred_slug:
            self.preferred_slug = slugify(self.preferred_slug)
            self.slug = self.preferred_slug
        else:
            self.slug = slugify(self.name)

    def save(self, *args, **kwargs):
        super(DynamicColumn, self).save(*args, **kwargs)

    def __str__(self):
        if self.location.isdigit():
            location = int(self.location)
        else:
            location = self.location

        return "{} ({})".format(
            self.name, dict(dcolumn_manager.css_containers).get(location, '')
            ).encode('utf-8')

    class Meta:
        ordering = ('location', 'order', 'name',)
        verbose_name = _("Dynamic Column")
        verbose_name_plural = _("Dynamic Columns")

    def get_choice_relation_object_and_field(self):
        return dcolumn_manager.get_relation_model_field(self.relation)


#
# ColumnCollection
#
class ColumnCollectionManager(StatusModelManagerMixin):

    def get_column_collection(self, name, unassigned=False):
        """
        Get the query set for the named collection. If unassigned is True add
        the unassigned dynamic columns to the query set.

        :Parameters:
            name : `str`
              Name of the column collection.
            unassigned : `bool`
              Also get items that are not assigned to a column collection yet.
        """
        log.debug("Collection name: %s, unassigned: %s", name, unassigned)
        queryset = self.none()

        try:
            queryset = self.active().get(name=name).dynamic_column.active()
        except self.model.DoesNotExist:
            pass # This is caught in the form.

        if unassigned:
            queryset = queryset | DynamicColumn.objects.active().filter(
                column_collection=None)

        return queryset

    def serialize_columns(self, name, obj=None, by_slug=False):
        """
        Serialize the dynamic column for this named collection in an
        OrderedDict. If a model that uses dcolumns is in `obj` it's key/value
        pairs are also returned. OrderedDict items can be either `pk` or `slug`.

        :Parameters:
            name : `str`
              Name of the collection.
            obj : `object`
              Model object that uses dcolumns.
            by_slug : `bool`
              If False the OrderedDict items are keyed by the dynamic column's
              `pk`, if True the dynamic column's `slug` is used.
        """
        records = self.get_column_collection(name)
        result = OrderedDict()

        if obj:
            key_value_map = obj.serialize_key_value_pairs()

        if by_slug:
            key = 'slug'
        else:
            key = 'pk'

        for record in records:
            rec = result.setdefault(getattr(record, key), {})
            rec['pk'] = record.pk
            rec['name'] = record.name
            rec['slug'] = record.slug
            rec['value_type'] = record.value_type

            if record.relation:
                rec['relation'] = record.relation
                rec['store_relation'] = record.store_relation

            rec['required'] = record.required
            # We convert the list to a dict because css_container_map may
            # not be keyed with integers.
            if record.location.isdigit():
                location = int(record.location)
            else:
                location = record.location

            rec['location'] = dict(dcolumn_manager.css_containers).get(
                location, '')
            rec['order'] = record.order
            if obj: rec['value'] = key_value_map.get(record.pk, '')

        return result

    def get_active_relation_items(self, name):
        """
        Get a list of all active relation type choice items. The list is
        made up of the names of each item.
        """
        records = self.get_column_collection(name)
        return [dcolumn_manager.choice_relation_map.get(record.relation)
                for record in records if record.relation]

    def get_collection_choices(self, name, use_pk=False):
        """
        Returns a set of choices for a list of options on an HTML select tag.
        Normally the slug is returned as the option value, however if `use_pk`
        is `True` then the value attribute will get the pk of the record.
        """
        records = self.get_column_collection(name)
        choices = [(use_pk and r.pk or r.slug, r.name) for r in records]
        return choices


class ColumnCollection(TimeModelMixin, UserModelMixin, StatusModelMixin,
                       ValidateOnSaveMixin):
    name = models.CharField(
        verbose_name=_("Name"), unique=True, max_length=50,
        help_text=_("Enter a unique name for this record."))
    dynamic_column = models.ManyToManyField(
        DynamicColumn, verbose_name=_("Dynamic Columns"),
        related_name='column_collection')

    objects = ColumnCollectionManager()

    def save(self, *args, **kwargs):
        log.debug("kwargs: %s", kwargs)
        super(ColumnCollection, self).save(*args, **kwargs)

    def __str__(self):
        return "{}-{}".format(
            self.name, self.updated.isoformat()).encode('utf-8')

    class Meta:
        ordering = ('name',)
        verbose_name = _("Column Collection")
        verbose_name_plural = _("Column Collections")

    def process_dynamic_columns(self, dcs):
        """
        This method adds or removes dynamic columns to the collection.
        """
        if dcs:
            new_pks = [inst.pk for inst in dcs]
            old_pks = [inst.pk for inst in self.dynamic_column.all()]
            rem_pks = list(set(old_pks) - set(new_pks))
            # Remove unwanted dynamic_columns.
            self.dynamic_column.remove(
                *self.dynamic_column.filter(pk__in=rem_pks))
            # Add new dynamic_columns.
            add_pks = list(set(new_pks) - set(old_pks))
            new_dcs = DynamicColumn.objects.filter(pk__in=add_pks)
            self.dynamic_column.add(*new_dcs)


#
# CollectionBase
#
class CollectionBaseManagerBase(models.Manager):

    def get_all_slugs(self):
        """
        Returns all slug names in a list.
        """
        return [r.slug for r in DynamicColumn.objects.all().order_by('slug')]

    def get_all_fields(self):
        """
        Returns all field names in a list.
        """
        return [unicode(field.name)
                for field in self.model._meta.get_fields()
                if 'collection' not in field.name and
                field.name != 'keyvalue_pairs']

    def get_all_fields_and_slugs(self):
        """
        Returns all field names and the dynamic column slugs is a sorted list.
        """
        result = self.get_all_slugs() + self.get_all_fields()
        result.sort()
        return result


class CollectionBase(TimeModelMixin, UserModelMixin, StatusModelMixin):
    column_collection = models.ForeignKey(
        ColumnCollection, verbose_name=_("Column Collection"),
        help_text=_("Choose the version of the dynamic columns you want "
                    "for all Collections."))

    def save(self, *args, **kwargs):
        log.debug("kwargs: %s", kwargs)
        super(CollectionBase, self).save(*args, **kwargs)

    def serialize_key_value_pairs(self, by_slug=False):
        """
        Returns a dict of the dynamic column PK and value.
        """
        result = {}

        if by_slug:
            field = 'slug'
        else:
            field = 'pk'

        for kv in self.keyvalue_pairs.all():
            result[getattr(kv.dynamic_column, field)] = kv.value.encode('utf-8')

        return result

    def get_dynamic_column(self, slug):
        """
        Gets the dynamic column given the column's slug.
        """
        try:
            dc = self.column_collection.dynamic_column.get(slug=slug)
        except DynamicColumn.DoesNotExist as e:
            log.error("DynamicColumn with slug '%s' does not exist.", slug)
            # Cannot get a dynamic column if not in a collection.
            dc = None

        return dc

    def get_key_value_pair(self, slug, field=None):
        """
        Return the KeyValue object value for the slug.
        """
        dc = self.get_dynamic_column(slug)

        try:
            obj = self.keyvalue_pairs.get(dynamic_column=dc)
        except self.keyvalue_pairs.model.DoesNotExist:
            log.error("Could not find value for slug '%s'.", slug)
            value = ''
        else:
            model_meta = dc.get_choice_relation_object_and_field()

            if dc.value_type == dc.CHOICE:
                if model_meta:
                    model, m_field = model_meta

                    if not field:
                        field = m_field

                    if dc.store_relation:
                        value = obj.value.encode('utf-8')
                    else:
                        value = model.objects.get_value_by_pk(obj.value, field)
            elif dc.value_type == dc.TIME:
                dt = dateutil.parser.parse(obj.value)
                value = datetime.time(
                    hour=dt.hour, minute=dt.minute, second=dt.second,
                    microsecond=dt.microsecond, tzinfo=dt.tzinfo)
            elif dc.value_type == dc.DATE:
                dt = dateutil.parser.parse(obj.value)
                value = datetime.date(year=dt.year, month=dt.month, day=dt.dat)
            elif dc.value_type == dc.DATETIME:
                value = dateutil.parser.parse(obj.value)
            elif dc.value_type == dc.BOOLEAN:
                if obj.value.isdigit() and obj.value == '0':
                    value = False
                elif obj.value.isdigit() and obj.value != '0':
                    value = True
                elif obj.value.lower() == 'false':
                    value = False
                elif obj.value.lower() == 'true':
                    value = True
            elif dc.value_type == dc.NUMBER and obj.value.isdigit():
                value = int(obj.value)
            elif (dc.value_type == dc.FLOAT and
                  obj.value.replace('.', '').isdigit()):
                value = float(obj.value)
            elif dc.value_type in (dc.TEXT, dc.TEXT_BLOCK):
                value = obj.value.encode('utf-8')
            else:
                msg = "Invalid value {}, should be type {}".format(
                        value, VALUE_TYPES_MAP.get(dc.value_type))
                log.error(msg)
                raise TypeError(msg)

        return value

    def set_key_value_pair(self, slug, value, field='', force=False):
        """
        This method sets an arbitrary key/value pair, it will log an error
        if the key/value pair could not be found.

        If the argument value contains the value 'increment' or 'decrement'
        the value associated with the slug will be incremented or decremented.

        Arguments:
          slug  -- The slug associated with the key value pair.
          value -- The value can be text or an object to get the value from.
          field -- The field used to get the value on the object.
          force -- Default is False, do not save empty strings or None objects
                   else True save empty strings only.
        """
        if (force and value == '') or value not in (None, ''):
            dc = self.get_dynamic_column(slug)

            if dc:
                if dc.value_type == dc.CHOICE and dc.store_relation and field:
                    value = getattr(value, field)
                elif dc.value_type == dc.CHOICE and hasattr(value, field):
                    value = getattr(value, field)
                elif dc.value_type == dc.CHOICE and hasattr(value, 'pk'):
                    value = value.pk
                elif (dc.value_type in (dc.TIME, dc.DATE, dc.DATETIME) and
                      isinstance(value, (datetime.time, datetime.date,
                                         datetime.datetime))):
                    value = value.isoformat()
                elif (dc.value_type in (dc.BOOLEAN, dc.FLOAT, dc.NUMBER) and
                      isinstance(value, (int, long, bool, float))):
                    value = str(value)
                elif (dc.value_type == dc.NUMBER and
                      value in ('increment', 'decrement')):
                    pass
                elif (dc.value_type in (dc.TEXT, dc.TEXT_BLOCK) and
                      isinstance(value, types.StringTypes)):
                    pass
                else:
                    msg = "Invalid value {}, should be type {}".format(
                        value, VALUE_TYPES_MAP.get(dc.value_type))
                    log.error(msg)
                    raise TypeError(msg)

                value = value.encode('utf-8')
                kv, created = self.keyvalue_pairs.get_or_create(
                    dynamic_column=dc, defaults={'value': value})

                if not created:
                    if 'increment' == value and kv.value.isdigit():
                        value = int(kv.value) + 1
                    elif 'decrement' == value and kv.value.isdigit():
                        value = int(kv.value) - 1

                    kv.value = value
                    kv.save()


#
# KeyValue
#
class KeyValueManager(models.Manager):
    pass


class KeyValue(ValidateOnSaveMixin):
    collection = models.ForeignKey(
        CollectionBase, verbose_name=_("Collection Type"),
        related_name='keyvalue_pairs')
    dynamic_column = models.ForeignKey(
        DynamicColumn, verbose_name=_("Dynamic Column"),
        related_name='keyvalue_pairs')
    value = models.TextField(verbose_name=_("Value"), null=True, blank=True)

    objects = KeyValueManager()

    def save(self, *args, **kwargs):
        super(KeyValue, self).save(*args, **kwargs)

    def __str__(self):
        return self.value.encode('utf-8')

    class Meta:
        ordering = ('dynamic_column__location', 'dynamic_column__order',)
        verbose_name = _("Key Value")
        verbose_name_plural = _("Key Values")
