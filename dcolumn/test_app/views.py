#
# dcolumn/test_app/views.py
#

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, CreateView, UpdateView, ListView

from dcolumn.dcolumns.views import (
    CollectionCreateUpdateViewMixin, CollectionDetailViewMixin)

from example_site.books.models import Book

from .forms import TestBookForm


#
# TestBookCreateView
#
class TestBookCreateView(LoginRequiredMixin,
                         CollectionCreateUpdateViewMixin,
                         CreateView):
    template_name = 'test_book_create_view.html'
    form_class = TestBookForm
    model = Book

    def get_success_url(self):
        url = reverse('test-book-detail', kwargs={'pk': self.object.pk})
        url += '?created=true'
        return url

test_book_create_view = TestBookCreateView.as_view()


#
# TestBookUpdateView
#
class TestBookUpdateView(LoginRequiredMixin,
                         CollectionCreateUpdateViewMixin,
                         UpdateView):
    template_name = 'test_book_create_view.html'
    form_class = TestBookForm
    model = Book

    def get_success_url(self):
        url = reverse('test-book-detail', kwargs={'pk': self.object.pk})
        url += '?updated=true'
        return url

test_book_update_view = TestBookUpdateView.as_view()


#
# TestBookDetailView
#
class TestBookDetailView(LoginRequiredMixin,
                         CollectionDetailViewMixin,
                         DetailView):
    template_name = 'test_book_detail_view.html'
    model = Book

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(TestBookDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        book = kwargs.get('object')
        pk = book and book.id or 0
        actions = [
            {'name': 'Create a New Book Entry',
             'url': reverse('test-book-create')},
            {'name': 'Edit this Book Entry',
             'url': reverse('test-book-update', args=(pk,))},
            ]
        context['actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in ('created', 'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, ''))

        context['info_message'] = info_message
        return context

test_book_detail_view = TestBookDetailView.as_view()


#
# TestBookListView
#
class TestBookListView(LoginRequiredMixin,
                       ListView):
    template_name = 'test_book_list_view.html'
    model = Book
    paginate_by = 50

test_book_list_view = TestBookListView.as_view()
