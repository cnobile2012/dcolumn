#
# example_site/books/models.py
#

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch

from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin,
    BaseChoiceModelManager)
from dcolumn.dcolumns.models import CollectionBase, CollectionBaseManagerBase

from .choices import Language


log = logging.getLogger('example_site.models')


#
# Promotion
#
class PromotionManager(BaseChoiceModelManager, StatusModelManagerMixin):

    def dynamic_column(self, active=True):
        """
        We need to return all choices even if some are inactive, because
        the store_relation field in DynamicColumn' is acive for this model.
        """
        return self.active(active=active)

    def get_choice_map(self, field, active=True):
        return dict([(getattr(obj, field), obj.pk)
                     for obj in self.dynamic_column(active=active)])


class Promotion(UserModelMixin, TimeModelMixin, StatusModelMixin):
    name = models.CharField(
        verbose_name=_(u"Promotion's Name"), max_length=250,
        help_text=_(u"Enter the name of the promotion."))
    description = models.TextField(
        verbose_name=_(u"Description"),
        help_text=_(u"Enter a description of the book promotion."))
    start_date = models.DateTimeField(
        verbose_name=_(u"Start Date & Time"), null=True, blank=True,
        help_text=_(u"Enter the start date and time of this promotion."))
    end_date = models.DateTimeField(
        verbose_name=_(u"End Date & Time"), null=True, blank=True,
        help_text=_(u"Enter the end date and time of this promotion."))

    objects = PromotionManager()

    class Meta:
        ordering = ('-start_date', 'name',)
        verbose_name = _(u"Promotion")
        verbose_name_plural = _(u"Promotions")

    def save(self, *args, **kwargs):
        super(Promotion, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"{}-{}".format(self.name, self.start_date.isoformat())

    def get_absolute_url(self):
        return reverse('promotion-detail', kwargs={u'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">View Page</a>'.format(self.get_absolute_url())
    _detail_producer.short_description = _(u"View Detail")
    _detail_producer.allow_tags = True


#
# Author
#
class AuthorManager(CollectionBaseManagerBase, StatusModelManagerMixin,
                    BaseChoiceModelManager):

    def dynamic_column(self, active=True):
        return self.active(active=active)

    def get_choice_map(self, field, active=True):
        return dict([(getattr(obj, field), obj.pk)
                     for obj in self.dynamic_column(active=active)])


class Author(CollectionBase):
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
        return reverse('author-detail', kwargs={u'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">View Page</a>'.format(self.get_absolute_url())
    _detail_producer.short_description = _(u"View Detail")
    _detail_producer.allow_tags = True


#
# Publisher
#
class PublisherManager(CollectionBaseManagerBase, StatusModelManagerMixin,
                       BaseChoiceModelManager):

    def dynamic_column(self, active=True):
        return self.active(active=active)

    def get_choice_map(self, field, active=True):
        return dict([(getattr(obj, field), obj.pk)
                     for obj in self.dynamic_column(active=active)])


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
        return reverse('publisher-detail', kwargs={u'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">View Page</a>'.format(self.get_absolute_url())
    _detail_producer.short_description = _(u"View Detail")
    _detail_producer.allow_tags = True

#
# Book
#
class BookManager(CollectionBaseManagerBase, StatusModelManagerMixin,
                  BaseChoiceModelManager):

    def dynamic_column(self, active=True):
        return self.active(active=active)

    def get_choice_map(self, field, active=True):
        return dict([(getattr(obj, field), obj.pk)
                     for obj in self.dynamic_column(active=active)])


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
        return reverse('book-detail', kwargs={u'pk': self.pk})

    def _detail_producer(self):
        return u'<a href="{}">View Page</a>'.format(self.get_absolute_url())
    _detail_producer.short_description = _(u"View Detail")
    _detail_producer.allow_tags = True
