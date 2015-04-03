#
# dcolumn/dcolumns/models.py
#

"""
Dynamic Column depended models

by: Carl J. Nobile

email: carl.nobile@gmail.com
"""
__docformat__ = "restructuredtext en"

import logging
from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin)

from .manager import dcolumn_manager

log = logging.getLogger('dcolumn.models')


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


class DynamicColumn(TimeModelMixin, UserModelMixin, StatusModelMixin):
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
        help_text=_(u"If you don't want the slug to change when the name "
                    u"changes enter a slug here. However, if you change this "
                    u"field the slug will track it."))
    slug = models.SlugField(
        verbose_name=_("Slug"), editable=False,
        help_text=_(u"This field is normally created from the name field, "
                    u"however, if you want to prevent it from changing when "
                    u"the name changes enter a preferred slug above."))
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
    location = models.IntegerField(
        verbose_name=_("Display Location"),
        choices=dcolumn_manager.css_containers,
        help_text=_("Choose a display location."))
    order = models.PositiveSmallIntegerField(verbose_name='Display Order')

    objects = DynamicColumnManager()

    class Meta:
        ordering = ('location', 'order', 'name',)
        verbose_name = _("Dynamic Column")
        verbose_name_plural = _("Dynamic Columns")

    def save(self):
        if self.preferred_slug:
            self.slug = self.preferred_slug
        else:
            self.slug = slugify(self.name)

        super(DynamicColumn, self).save()

    def __unicode__(self):
        return self.name

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
        records = self.get_column_collection(name)
        result = OrderedDict()

        if obj:
            key_value_map = obj.serialize_key_value_pairs()

        if by_slug:
            key = u'slug'
        else:
            key = u'pk'

        for record in records:
            rec = result.setdefault(getattr(record, key), {})
            rec[u'pk'] = record.pk
            rec[u'name'] = record.name
            rec[u'slug'] = record.slug
            rec[u'value_type'] = record.value_type

            if record.relation:
                rec[u'relation'] = record.relation
                rec[u'store_relation'] = record.store_relation

            rec[u'required'] = record.required
            # We convert the list to a dict because css_container_map may
            # not be keyed with integers.
            rec[u'location'] = dict(dcolumn_manager.css_containers).get(
                record.location, u'')
            rec[u'order'] = record.order
            if obj: rec[u'value'] = key_value_map.get(record.pk, u'')

        return result

    def get_active_relation_items(self, name):
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


class ColumnCollection(TimeModelMixin, UserModelMixin, StatusModelMixin):
    name = models.CharField(
        verbose_name=_("Name"), unique=True, max_length=50,
        help_text=_("Enter a unique name for this record."))
    dynamic_column = models.ManyToManyField(
        DynamicColumn, verbose_name=_("Dynamic Column"),
        related_name='column_collection')

    objects = ColumnCollectionManager()

    class Meta:
        verbose_name = _("Column Collection")
        verbose_name_plural = _("Column Collections")

    def __unicode__(self):
        return u"{}-{}".format(self.name, self.updated.isoformat())

    def save(self, *args, **kwargs):
        log.debug("kwargs: %s", kwargs)
        super(ColumnCollection, self).save(*args, **kwargs)


#
# CollectionBase
#
class CollectionBaseManagerBase(models.Manager):

    def get_all_slugs(self):
        return [r.slug for r in DynamicColumn.objects.all().order_by('slug')]

    def get_all_fields(self):
        return [unicode(field)
                for field in self.model._meta.get_all_field_names()
                if u'collection' not in field and field != u'keyvalue_pairs']

    def get_all_fields_and_slugs(self):
        result = self.get_all_slugs() + self.get_all_fields()
        result.sort()
        return result


class CollectionBase(TimeModelMixin, UserModelMixin, StatusModelMixin):
    column_collection = models.ForeignKey(
        ColumnCollection, verbose_name=_("Column Collection"),
        help_text=_(u"Choose the version of the dynamic columns you want "
                    u"for all Collections."))

    def save(self, *args, **kwargs):
        log.debug("kwargs: %s", kwargs)
        super(CollectionBase, self).save(*args, **kwargs)

    def serialize_key_value_pairs(self):
        result = {}

        for kv in self.keyvalue_pairs.all():
            result[kv.dynamic_column_id] = kv.value

        return result

    def get_dynamic_column(self, slug):
        try:
            dc = self.column_collection.dynamic_column.get(slug=slug)
        except DynamicColumn.DoesNotExist as e:
            log.error("DynamicColumn with slug '%s' does not exist.", slug)
            # Cannot get a dynamic column if not in the collection already.
            dc = None

        return dc

    def get_key_value_pair(self, slug, field='value'):
        dc = self.get_dynamic_column(slug)

        try:
            obj = self.keyvalue_pairs.get(dynamic_column=dc)

            model_meta = dc.get_choice_relation_object_and_field()

            if model_meta and not dc.store_relation:
                model, notused = model_meta
                value = model.objects.get_value_by_pk(obj.value, field=field)
            else:
                value = obj.value
        except self.keyvalue_pairs.model.DoesNotExist as e:
            log.error("Could not find value for slug '%s'.", slug)
            value = u''

        return value

    def set_key_value_pair(self, slug, value, field=None, force=False):
        """
        This method sets an arbitrary key/value pair, it will log an error
        if the key/value pair could not be found.

        If value contains the value 'increment' or 'decrement' the value
        associated with the slug will be incremented or decremented.

        Arguments:
          slug  -- The slug associated with the key value pair.
          value -- The value can be text or an object to get the value from.
          field -- The field used to get the value on the object.
          force -- Default is False, do not save empty strings or None objects
                   else True save empty strings only.
        """
        if (force and value == u'') or value not in (None, u''):
            dc = self.get_dynamic_column(slug)

            if dc:
                if dc.store_relation and field:
                    value = getattr(value, field)
                elif hasattr(value, field):
                    value = getattr(value, field)
                elif hasattr(value, u'pk'):
                    value = value.pk
                elif isinstance(value, (datetime.datetime, datetime.date)):
                    value = value.strftime(u"%Y-%m-%d")

                kv, created = self.keyvalue_pairs.get_or_create(
                    dynamic_column=dc, defaults={u'value': value})

                if not created:
                    if u'increment' == value and kv.value.isdigit():
                        value = int(kv.value) + 1
                    elif u'decrement' == value and kv.value.isdigit():
                        value = int(kv.value) - 1

                    kv.value = value
                    kv.save()


#
# KeyValue
#
class KeyValueManager(models.Manager):
    pass


class KeyValue(models.Model):
    collection = models.ForeignKey(
        CollectionBase, verbose_name=_("Collection Type"),
        related_name='keyvalue_pairs')
    dynamic_column = models.ForeignKey(
        DynamicColumn, verbose_name=_("Dynamic Column"),
        related_name='keyvalue_pairs')
    value = models.TextField(verbose_name=_("Value"), null=True, blank=True)

    objects = KeyValueManager()

    class Meta:
        ordering = ('dynamic_column__location', 'dynamic_column__order',)
        verbose_name = _("Key Value")
        verbose_name_plural = _("Key Values")

    def __unicode__(self):
        return self.value
