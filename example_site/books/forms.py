#
# example_site/books/forms.py
#

import logging

from django import forms

from dcolumn.dcolumns.forms import CollectionBaseFormMixin

from .models import Promotion, Author, Publisher, Book

log = logging.getLogger('examples.books.views')


#
# Promotion
#
class PromotionForm(CollectionBaseFormMixin):

    def __init__(self, *args, **kwargs):
        super(PromotionForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields['name'].widget = forms.TextInput(
            attrs={'size': 100, 'maxlength': 250})
        # Gets rid of the annoying colon after every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = ''

    class Meta:
        model = Promotion
        exclude = ('creator', 'updater', 'created', 'updated',)

    class Media:
        css = {
            'all': ('css/promotions.css',)
            }


#
# Author
#
class AuthorForm(CollectionBaseFormMixin):

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields['name'].widget = forms.TextInput(
            attrs={'size': 50, 'maxlength': 250})
        # Gets rid of the annoying colon after every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = ''

    class Meta:
        model = Author
        exclude = CollectionBaseFormMixin.Meta.exclude


#
# Publisher
#
class PublisherForm(CollectionBaseFormMixin):

    def __init__(self, *args, **kwargs):
        super(PublisherForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields['name'].widget = forms.TextInput(
            attrs={'size': 50, 'maxlength': 250})
        # Gets rid of the annoying colon after every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = ''

    class Meta:
        model = Publisher
        exclude = CollectionBaseFormMixin.Meta.exclude


#
# Book
#
class BookForm(CollectionBaseFormMixin):

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields['title'].widget = forms.TextInput(
            attrs={'size': 80, 'maxlength': 250})
        # Gets rid of the annoying colon after every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = ''

    class Meta:
        model = Book
        exclude = CollectionBaseFormMixin.Meta.exclude
