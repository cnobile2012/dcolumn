#
# example_site/books/models.py
#

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin)
from dcolumn.dcolumns.models import CollectionBase

from .choices import Language


log = logging.getLogger('example_site.models')


#
# Author
#
class AuthorManager(StatusModelManagerMixin):

    def dynamic_column(self):
        return self.active()


class Author(CollectionBase):
    name = models.CharField(
        verbose_name=_("Author's Name"), max_length=250,
        help_text=_("Enter the name of the author."))

    objects = AuthorManager()

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def save(self, *args, **kwargs):
        super(Author, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode("{}".format(self.name))

    def get_absolute_url(self):
        return reverse('author-detail', kwargs={'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">View Page</a>'.format(self.get_absolute_url())
    _detail_producer.short_description = "View Detail"
    _detail_producer.allow_tags = True


#
# Publisher
#
class PublisherManager(StatusModelManagerMixin):

    def dynamic_column(self):
        return self.active()


class Publisher(CollectionBase):
    name = models.CharField(
        verbose_name=_("Publisher's Name"), max_length=250,
        help_text=_("Enter the name of the publisher."))

    objects = PublisherManager()

    class Meta:
        verbose_name = _("Publisher")
        verbose_name_plural = _("Publishers")

    def save(self, *args, **kwargs):
        super(Publisher, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode("{}".format(self.name))

    def get_absolute_url(self):
        return reverse('publisher-detail', kwargs={'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">View Page</a>'.format(self.get_absolute_url())
    _detail_producer.short_description = "View Detail"
    _detail_producer.allow_tags = True

#
# Book
#
class BookManager(StatusModelManagerMixin):

    def dynamic_column(self):
        return self.active()


class Book(CollectionBase):
    title = models.CharField(
        verbose_name=_("Title"), max_length=250,
        help_text=_("Enter a book title."))

    objects = BookManager()

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def save(self, *args, **kwargs):
        super(Book, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode("{}".format(self.title))

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">View Page</a>'.format(self.get_absolute_url())
    _detail_producer.short_description = "View Detail"
    _detail_producer.allow_tags = True
