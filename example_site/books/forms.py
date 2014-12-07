#
# example_site/books/forms.py
#

import logging

from django import forms

from dcolumn.dcolumns.forms import CollectionFormMixin
from dcolumn.dcolumns.manager import dcolumn_manager

from .models import Promotion, Author, Publisher, Book

dcolumn_manager.register_choice(Promotion, 2, u'name')
dcolumn_manager.register_choice(Author, 3, u'name')
dcolumn_manager.register_choice(Publisher, 4, u'name')
dcolumn_manager.register_choice(Book, 5, u'title')

log = logging.getLogger('example_site.views')


#
# Promotion
#
class PromotionForm(CollectionFormMixin):

    def __init__(self, *args, **kwargs):
        super(PromotionForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields[u'name'].widget = forms.TextInput(
            attrs={u'size': 100, u'maxlength': 250})
        # Gets rid of the annoying colon afer every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = u''

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
class AuthorForm(CollectionFormMixin):

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields[u'name'].widget = forms.TextInput(
            attrs={u'size': 50, u'maxlength': 250})
        # Gets rid of the annoying colon afer every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = u''

    class Meta:
        model = Author
        exclude = CollectionFormMixin.Meta.exclude


#
# Publisher
#
class PublisherForm(CollectionFormMixin):

    def __init__(self, *args, **kwargs):
        super(PublisherForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields[u'name'].widget = forms.TextInput(
            attrs={u'size': 50, u'maxlength': 250})
        # Gets rid of the annoying colon afer every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = u''

    class Meta:
        model = Publisher
        exclude = CollectionFormMixin.Meta.exclude


#
# Book
#
class BookForm(CollectionFormMixin):

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        log.debug("args: %s, kwargs: %s", args, kwargs)
        self.fields[u'title'].widget = forms.TextInput(
            attrs={u'size': 50, u'maxlength': 250})
        # Gets rid of the annoying colon afer every label, but only works on
        # Django 1.6 and above.
        self.label_suffix = u''

    class Meta:
        model = Book
        exclude = CollectionFormMixin.Meta.exclude
