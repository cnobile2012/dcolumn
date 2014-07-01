#
# example_site/books/views.py
#

import logging

from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from dcolumn.dcolumns.views import (
    CollectionCreateUpdateViewMixin, CollectionDetailViewMixin)

from .models import Book
from .forms import BookForm


#
# BookCreateView
#
class BookCreateView(CreateView, CollectionCreateUpdateViewMixin):
    template_name = u'books/book_create_view.html'
    form_class = BookForm
    model = Book

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?created=true'
        return url

book_create_view = BookCreateView.as_view()


#
# BookUpdateView
#
class BookUpdateView(UpdateView, CollectionCreateUpdateViewMixin):
    template_name = u'books/book_create_view.html'
    form_class = BookForm
    model = Book

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?updated=true'
        return url

book_update_view = BookUpdateView.as_view()


#
# BookDetailView
#
class BookDetailView(DetailView, CollectionDetailViewMixin):
    template_name = u'books/book_detail_view.html'
    model = Book

    def get_context_data(self, **kwargs):
        """
        Get context data for the Parent KeyValue objects.
        """
        context = super(BookDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        parent = kwargs.get(u'object')
        pk = parent and parent.id or 0
        actions = [
            {u'name': u'Create a New Record',
             u'url': reverse(u'parent-create')},
            {u'name': u'Edit this Record',
             u'url': reverse(u'parent-update', args=(pk,))},
            ]
        context[u'actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in (u'created', u'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, u''))

        context[u'info_message'] = info_message
        return context

book_detail_view = BookDetailView.as_view()
