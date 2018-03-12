#
# example_site/books/models.py
#
from __future__ import unicode_literals

import logging

from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin,
    ValidateOnSaveMixin)
from dcolumn.dcolumns.models import CollectionBase, CollectionBaseManager
from dcolumn.dcolumns.manager import dcolumn_manager

from .choices import Language


log = logging.getLogger('examples.books.models')


#
# Promotion
#
class PromotionManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


@python_2_unicode_compatible
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('promotion-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return format_html('<a href="{}">View Page</a>',
                           self.get_absolute_url())
    detail_producer.short_description = _("View Detail")


#
# Author
#
class AuthorManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


@python_2_unicode_compatible
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('author-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return format_html('<a href="{}">View Page</a>',
                           self.get_absolute_url())
    detail_producer.short_description = _("View Detail")


#
# Publisher
#
class PublisherManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


@python_2_unicode_compatible
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('publisher-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return format_html('<a href="{}">View Page</a>',
                           self.get_absolute_url())
    detail_producer.short_description = _("View Detail")


#
# Book
#
class BookManager(CollectionBaseManager, StatusModelManagerMixin):
    pass


@python_2_unicode_compatible
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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    def detail_producer(self):
        return format_html('<a href="{}">View Page</a>',
                           self.get_absolute_url())
    detail_producer.short_description = _("View Detail")


dcolumn_manager.register_choice(Promotion, 2, 'name')
dcolumn_manager.register_choice(Author, 3, 'name')
dcolumn_manager.register_choice(Publisher, 4, 'name')
dcolumn_manager.register_choice(Book, 5, 'title')
