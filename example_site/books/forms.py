#
# example_site/books/forms.py
#

import logging

from django import forms

from dcolumn.dcolumns.forms import CollectionFormMixin
from dcolumn.dcolumns.manager import dcolumn_manager

from .models import Author, Publisher, Book

dcolumn_manager.register_choice(Author, 2, u'name')
dcolumn_manager.register_choice(Publisher, 3, u'name')
dcolumn_manager.register_choice(Book, 4, u'title')


#
# Author
#
class AuthorForm(CollectionFormMixin):

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Author


#
# Publisher
#
class PublisherForm(CollectionFormMixin):

    def __init__(self, *args, **kwargs):
        super(PublisherForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Publisher


#
# Book
#
class BookForm(CollectionFormMixin):

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Book
