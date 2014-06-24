#
# dcolumn/dynamic_columns/models.py
#

import logging
from collections import OrderedDict

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from dcolumn.settings import DYNAMIC_COLUMN_ITEM_NAME
from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin)
from .choices import Language
from .manage import choice_manager

log = logging.getLogger('dcolumn.models')


#
# Book
#
class BookManager(StatusModelManagerMixin):

    def dynamic_column(self):
        return self.active()


class Book(UserModelMixin, TimeModelMixin, StatusModelMixin):
    title = models.TextField(
        verbose_name=_("Title"), help_text=_("Enter a book title."))
    author = models.TextField(
        verbose_name=_("Author"), help_text=_("Enter the author of this book."))
    publisher = models.TextField(
        verbose_name=_("Publisher"),
        help_text=_("Enter the publisher of this book."))
    isbn10 = models.TextField(
        verbose_name=_("ISBN-10"), null=True, blank=True,
        help_text=_("Enter the book ISBN-10 code."))
    isbn13 = models.TextField(
        verbose_name=_("ISBN-13"), help_text=_("Enter the book ISBN-13 code."))

    objects = BookManager()

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __unicode__(self):
        return self.title

choice_manager.register_choice(Book, 2, u'title')


#
# DynamicColumn
#
class DynamicColumnManager(StatusModelManagerMixin):

    def get_fk_slugs(self):
        result = {}

        for record in self.active():
            if record.value_type == self.model.CHOICE:
                name = choice_manager.choice_relation_map.get(record.relation)
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

    name = models.TextField(
        verbose_name=_("Name"), help_text=_("Enter a column name."))
    slug = models.SlugField(verbose_name=_("Slug"), editable=False)
    value_type = models.IntegerField(
        verbose_name=_("Value Type"), choices=VALUE_TYPES,
        help_text=_("Choose the value type."))
    relation = models.IntegerField(
        verbose_name=_("Choice Relation"),
        choices=choice_manager.choice_relation,
        null=True, blank=True, help_text=_("Choose the Choice Relation type."))
    required = models.BooleanField(verbose_name=_("Required Field"))
    location = models.IntegerField(
        verbose_name=_("Display Location"),
        choices=choice_manager.css_containers,
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
            result = choice_manager.choice_relation_map.get(self.relation, '')

        return result
    _relation_producer.short_description = _("Relation")


#
# DynamicColumnItem
#
class DynamicColumnItemManager(StatusModelManagerMixin):

    def get_dynamic_columns(self, name):
        try:
            return self.active().get(name=name).dynamic_column.active(
                ).order_by('location', 'order', 'name')
        except self.model.DoesNotExist:
            msg = ("No objects in database, please create initial objects "
                   "for Dynamic Columns and Dynamic Column Items")
            log.error(msg)
            raise self.model.DoesNotExist(msg)

    def serialize_columns(self, obj=None):
        records = self.get_dynamic_columns(DYNAMIC_COLUMN_ITEM_NAME)
        result = OrderedDict()

        if obj:
            key_value_map = obj.serialize_key_value_pairs()

        for record in records:
            rec = result.setdefault(record.pk, {})
            rec[u'name'] = record.name
            rec[u'slug'] = record.slug
            rec[u'value_type'] = record.value_type
            rec[u'relation'] = record.relation
            rec[u'required'] = record.required
            # We convert the list to a dict because css_container_map may
            # not be keyed with integers.
            rec[u'location'] = dict(choice_manager.css_containers).get(
                record.location, u'')
            rec[u'order'] = record.order
            if obj: rec[u'value'] = key_value_map.get(record.pk, u'')

        return result

    def get_active_relation_items(self):
        records = self.get_dynamic_columns(DYNAMIC_COLUMN_ITEM_NAME)
        return [choice_manager.choice_relation_map.get(record.relation)
                for record in records if record.relation]


class DynamicColumnItem(UserModelMixin, TimeModelMixin, StatusModelMixin):
    name = models.TextField(
        verbose_name=_("Name"), unique=True,
        help_text=_("Enter a unique name for this record."))
    dynamic_column = models.ManyToManyField(
        DynamicColumn, verbose_name=_("Dynamic Column"),
        related_name='dynamic_column_items')

    objects = DynamicColumnItemManager()

    class Meta:
        verbose_name = _("Dynamic Column Item")
        verbose_name_plural = _("Dynamic Column Items")

    def __unicode__(self):
        return unicode("{}-{}".format(self.name, self.mtime.isoformat()))


#
# Parent (Any model you need to have predefined key/value pairs on.)
#
class ParentManager(StatusModelManagerMixin):
    pass


class Parent(UserModelMixin, TimeModelMixin, StatusModelMixin):
    name = models.TextField(
        verbose_name=_("Name"), unique=True,
        help_text=_("Enter a unique name for this record."))
    dynamic_column_item = models.ForeignKey(
        DynamicColumnItem, verbose_name=_("Dynamic Column Item"),
        help_text=_(u"Choose the version of the dynamic columns you want "
                    u"for all Patents."))

    objects = ParentManager()

    class Meta:
        verbose_name = _("Parent")
        verbose_name_plural = _("Parents")

    def __unicode__(self):
        return unicode("{}".format(self.name))

    def get_absolute_url(self):
        return reverse('parent-detail', kwargs={'pk': self.pk})

    def serialize_key_value_pairs(self):
        result = {}

        for kv in self.keyvalue_pairs.all():
            result[kv.dynamic_column_id] = kv.value

        return result

    def _detail_producer(self):
        return u'<a href="{}">{}</a>'.format(self.get_absolute_url(), self)
    _detail_producer.short_description = "View Detail"
    _detail_producer.allow_tags = True

    def find_key_value(self, name):
        # FIX ME -- This needs to find the model named with 'name' then return
        # the value of that object, not the hand edited name in the
        # dynamic_column.
        record = self.keyvalue_pairs.filter(dynamic_column__name=name)
        result = u''

        if len(record) > 0:
            result = record[0].value

        return result


#
# KeyValue
#
class KeyValueManager(models.Manager):

    def set_parent_key_value_pairs(self, obj):
        for item in obj.dynamic_column_item.dynamic_column.all():
            self.create(parent=obj, dynamic_column=item)


class KeyValue(models.Model):
    parent = models.ForeignKey(
        Parent, verbose_name=_("Parent"), related_name='keyvalue_pairs')
    dynamic_column = models.ForeignKey(
        DynamicColumn, verbose_name=_("Dynamic Column"),
        related_name='keyvalue_pairs')
    value = models.TextField(verbose_name=_("Value"), null=True, blank=True)

    objects = KeyValueManager()

    class Meta:
        verbose_name = _("Key Value")
        verbose_name_plural = _("Key Values")

    def __unicode__(self):
        return unicode(self.parent)
