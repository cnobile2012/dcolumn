#
# example_site/books/models.py
#

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin)
from dcolumn.dcolumns.manager import dcolumn_manager
from dcolumn.dcolumns.models import CollectionMixin, KeyValueMixin

from .choices import Language


log = logging.getLogger('example_site.models')


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
        verbose_name=_("ISBN-13"), null=True, blank=True,
        help_text=_("Enter the book ISBN-13 code."))

    objects = BookManager()

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __unicode__(self):
        return self.title

dcolumn_manager.register_choice(Book, 2, u'title')


#
# Parent (Any model you need to have predefined key/value pairs on.)
#
class ParentManager(StatusModelManagerMixin):
    pass


class Parent(CollectionMixin, TimeModelMixin, UserModelMixin, StatusModelMixin):
    name = models.TextField(
        verbose_name=_("Name"), unique=True,
        help_text=_("Enter a unique name for this record."))

    objects = ParentManager()

    class Meta:
        verbose_name = _("Parent")
        verbose_name_plural = _("Parents")

    def __unicode__(self):
        return unicode("{}".format(self.name))

    def get_absolute_url(self):
        return reverse('parent-detail', kwargs={'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">{}</a>'.format(self.get_absolute_url(), self)
    _detail_producer.short_description = "View Detail"
    _detail_producer.allow_tags = True


#
# KeyValue
#
class KeyValueManager(models.Manager):

    def set_parent_key_value_pairs(self, obj):
        for item in obj.column_collection.dynamic_column.all():
            self.create(parent=obj, dynamic_column=item)


class KeyValue(KeyValueMixin):
    parent = models.ForeignKey(
        Parent, verbose_name=_("Parent"), related_name='keyvalue_pairs')

    def __unicode__(self):
        return unicode(self.parent)
