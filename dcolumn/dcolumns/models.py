#
# dcolumn/dcolumns/models.py
#

import logging
from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin)
from .manager import dcolumn_manager

log = logging.getLogger('dcolumn.models')


#
# DynamicColumn
#
class DynamicColumnManager(StatusModelManagerMixin):

    def get_fk_slugs(self):
        result = {}

        for record in self.active():
            if record.value_type == self.model.CHOICE:
                name = dcolumn_manager.choice_relation_map.get(record.relation)
                result[name] = record.slug

        return result


class DynamicColumn(UserModelMixin, TimeModelMixin, StatusModelMixin):
    BOOLEAN = 1
    CHOICE = 2
    DATE = 3
    FLOAT = 4
    NUMBER = 5
    TEXT = 6
    TEXT_BLOCK = 7
    VALUE_TYPES = (
        (BOOLEAN, _("Boolean")),
        (CHOICE, _("Choice")),
        (DATE, _("Date")),
        (FLOAT, _("Floating Point")),
        (NUMBER, _("Number")),
        (TEXT, _("Text")),
        (TEXT_BLOCK, _("Text Block")),
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
    slug = models.SlugField(verbose_name=_("Slug"), editable=False)
    value_type = models.IntegerField(
        verbose_name=_("Value Type"), choices=VALUE_TYPES,
        help_text=_("Choose the value type."))
    relation = models.IntegerField(
        verbose_name=_("Choice Relation"), null=True, blank=True,
        choices=dcolumn_manager.choice_relations,
        help_text=_("Choose the Choice Relation type."))
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


#
# ColumnCollection
#
class ColumnCollectionManager(StatusModelManagerMixin):

    def get_dynamic_columns(self, name):
        try:
            return self.active().get(name=name).dynamic_column.active(
                ).order_by('location', 'order', 'name')
        except self.model.DoesNotExist:
            msg = ("No objects in database, please create initial objects "
                   "for Dynamic Columns and Column Collections")
            log.error(msg)
            raise self.model.DoesNotExist(msg)

    def serialize_columns(self, obj=None):
        records = self.get_dynamic_columns(
            dcolumn_manager.get_default_column_name(u'Parent'))
        result = OrderedDict()

        if obj:
            key_value_map = obj.serialize_key_value_pairs()

        for record in records:
            rec = result.setdefault(record.pk, {})
            rec[u'name'] = record.name
            rec[u'slug'] = record.slug
            rec[u'value_type'] = record.value_type
            rec[u'relation'] = record.relation
            if record.relation: rec[u'store_relation'] = record.store_relation
            rec[u'required'] = record.required
            # We convert the list to a dict because css_container_map may
            # not be keyed with integers.
            rec[u'location'] = dict(dcolumn_manager.css_containers).get(
                record.location, u'')
            rec[u'order'] = record.order
            if obj: rec[u'value'] = key_value_map.get(record.pk, u'')

        return result

    def get_active_relation_items(self):
        records = self.get_dynamic_columns(
            dcolumn_manager.get_default_column_name(u'Parent'))
        return [dcolumn_manager.choice_relation_map.get(record.relation)
                for record in records if record.relation]


class ColumnCollection(UserModelMixin, TimeModelMixin, StatusModelMixin):
    name = models.CharField(
        verbose_name=_("Name"), unique=True, max_length=50,
        help_text=_("Enter a unique name for this record."))
    dynamic_column = models.ManyToManyField(
        DynamicColumn, verbose_name=_("Dynamic Column"),
        related_name='column_collections')

    objects = ColumnCollectionManager()

    class Meta:
        verbose_name = _("Column Collection")
        verbose_name_plural = _("Column Collections")

    def __unicode__(self):
        return unicode("{}-{}".format(self.name, self.mtime.isoformat()))


#
# CollectionBase
#
class CollectionBase(models.Model):
    column_collection = models.ForeignKey(
        ColumnCollection, verbose_name=_("Column Collection"),
        help_text=_(u"Choose the version of the dynamic columns you want "
                    u"for all Collections."))

#    class Meta:
#        abstract = True

    def save(self, *args, **kwargs):
        super(CollectionMixin, self).save(*args, **kwargs)

    def serialize_key_value_pairs(self):
        result = {}

        for kv in self.keyvalue_pairs.all():
            result[kv.dynamic_column_id] = kv.value

        return result

    ## def find_key_value(self, name):
    ##     # FIX ME -- This needs to find the model named with 'name' then return
    ##     # the value of that object, not the hand edited name in the
    ##     # dynamic_column.
    ##     record = self.keyvalue_pairs.filter(dynamic_column__name=name)
    ##     result = u''

    ##     if len(record) > 0:
    ##         result = record[0].value

    ##     return result


#
# KeyValue
#
class KeyValueManager(models.Manager):
    pass

    ## def set_parent_key_value_pairs(self, obj):
    ##     for item in obj.column_collection.dynamic_column.all():
    ##         self.create(parent=obj, dynamic_column=item)


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
        verbose_name = _("Key Value")
        verbose_name_plural = _("Key Values")

    def __unicode__(self):
        return unicode(self.collection)
