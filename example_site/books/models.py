#
# example_site/books/models.py
#

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin,
    ValidateOnSaveMixin)
from dcolumn.dcolumns.models import CollectionBase, CollectionBaseManager

from .choices import Language


log = logging.getLogger('examples.books.models')


#
# Promotion
#
class PromotionManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


class Promotion(CollectionBase, ValidateOnSaveMixin):
    name = models.CharField(
        verbose_name=_("Promotion's Name"), max_length=250,
        help_text=_("Enter the name of the promotion."))

    objects = PromotionManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _("Promotion")
        verbose_name_plural = _("Promotions")

    def save(self, *args, **kwargs):
        super(Promotion, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{}".format(self.name)

    def get_absolute_url(self):
        return reverse('promotion-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return '<a href="{}">View Page</a>'.format(self.get_absolute_url())
    detail_producer.short_description = _("View Detail")
    detail_producer.allow_tags = True


#
# Author
#
class AuthorManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


class Author(CollectionBase, ValidateOnSaveMixin):
    name = models.CharField(
        verbose_name=_("Author's Name"), max_length=250,
        help_text=_("Enter the name of the author."))

    objects = AuthorManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def save(self, *args, **kwargs):
        super(Author, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('author-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return '<a href="{}">View Page</a>'.format(self.get_absolute_url())
    detail_producer.short_description = _("View Detail")
    detail_producer.allow_tags = True


#
# Publisher
#
class PublisherManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


class Publisher(CollectionBase, ValidateOnSaveMixin):
    name = models.CharField(
        verbose_name=_("Publisher's Name"), max_length=250,
        help_text=_("Enter the name of the publisher."))

    objects = PublisherManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _("Publisher")
        verbose_name_plural = _("Publishers")

    def save(self, *args, **kwargs):
        super(Publisher, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode("{}".format(self.name))

    def get_absolute_url(self):
        return reverse('publisher-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return '<a href="{}">View Page</a>'.format(self.get_absolute_url())
    detail_producer.short_description = _("View Detail")
    detail_producer.allow_tags = True

#
# Book
#
class BookManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


class Book(CollectionBase, ValidateOnSaveMixin):
    title = models.CharField(
        verbose_name=_("Title"), max_length=250,
        help_text=_("Enter a book title."))

    objects = BookManager()

    class Meta:
        ordering = ('title',)
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def save(self, *args, **kwargs):
        super(Book, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode("{}".format(self.title))

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return '<a href="{}">View Page</a>'.format(self.get_absolute_url())
    detail_producer.short_description = _("View Detail")
    detail_producer.allow_tags = True
