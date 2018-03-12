#
# example_site/books/views.py
#

import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, CreateView, UpdateView, ListView

from dcolumn.dcolumns.views import (
    CollectionCreateUpdateViewMixin, CollectionDetailViewMixin)

from .models import Book, Publisher, Author, Promotion
from .forms import BookForm, PublisherForm, AuthorForm, PromotionForm

log = logging.getLogger('examples.books.views')


#
# BookCreateView
#
class BookCreateView(LoginRequiredMixin,
                     CollectionCreateUpdateViewMixin,
                     CreateView):
    template_name = 'books/book_create_view.html'
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
class BookUpdateView(LoginRequiredMixin,
                     CollectionCreateUpdateViewMixin,
                     UpdateView):
    template_name = 'books/book_create_view.html'
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
class BookDetailView(LoginRequiredMixin,
                     CollectionDetailViewMixin,
                     DetailView):
    template_name = 'books/book_detail_view.html'
    model = Book

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(BookDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        book = kwargs.get('object')
        pk = book and book.id or 0
        actions = [
            {'name': 'Create a New Book Entry',
             'url': reverse('book-create')},
            {'name': 'Edit this Book Entry',
             'url': reverse('book-update', args=(pk,))},
            ]
        context['actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in ('created', 'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, ''))

        context['info_message'] = info_message
        return context

book_detail_view = BookDetailView.as_view()


#
# BookListView
#
class BookListView(LoginRequiredMixin,
                   ListView):
    template_name = 'books/book_list_view.html'
    model = Book
    paginate_by = 50

book_list_view = BookListView.as_view()


#
# PublisherCreateView
#
class PublisherCreateView(LoginRequiredMixin,
                          CollectionCreateUpdateViewMixin,
                          CreateView):
    template_name = 'books/publisher_create_view.html'
    form_class = PublisherForm
    model = Publisher

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?created=true'
        return url

publisher_create_view = PublisherCreateView.as_view()


#
# PublisherUpdateView
#
class PublisherUpdateView(LoginRequiredMixin,
                          CollectionCreateUpdateViewMixin,
                          UpdateView):
    template_name = 'books/publisher_create_view.html'
    form_class = PublisherForm
    model = Publisher

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?updated=true'
        return url

publisher_update_view = PublisherUpdateView.as_view()


#
# PublisherDetailView
#
class PublisherDetailView(LoginRequiredMixin,
                          CollectionDetailViewMixin,
                          DetailView):
    template_name = 'books/publisher_detail_view.html'
    model = Publisher

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(PublisherDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        publisher = kwargs.get('object')
        pk = publisher and publisher.id or 0
        actions = [
            {'name': 'Create a New Publisher Entry',
             'url': reverse('publisher-create')},
            {'name': 'Edit this Publisher Entry',
             'url': reverse('publisher-update', args=(pk,))},
            ]
        context['actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in ('created', 'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, ''))

        context['info_message'] = info_message
        return context

publisher_detail_view = PublisherDetailView.as_view()


#
# PublisherListView
#
class PublisherListView(LoginRequiredMixin,
                        ListView):
    template_name = 'books/publisher_list_view.html'
    model = Publisher
    paginate_by = 50

publisher_list_view = PublisherListView.as_view()


#
# AuthorCreateView
#
class AuthorCreateView(LoginRequiredMixin,
                       CollectionCreateUpdateViewMixin,
                       CreateView):
    template_name = 'books/author_create_view.html'
    form_class = AuthorForm
    model = Author

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?created=true'
        return url

author_create_view = AuthorCreateView.as_view()


#
# AuthorUpdateView
#
class AuthorUpdateView(LoginRequiredMixin,
                       CollectionCreateUpdateViewMixin,
                       UpdateView):
    template_name = 'books/author_create_view.html'
    form_class = AuthorForm
    model = Author

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?updated=true'
        return url

author_update_view = AuthorUpdateView.as_view()


#
# AuthorDetailView
#
class AuthorDetailView(LoginRequiredMixin,
                       CollectionDetailViewMixin,
                       DetailView):
    template_name = 'books/author_detail_view.html'
    model = Author

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        author = kwargs.get('object')
        pk = author and author.id or 0
        actions = [
            {'name': 'Create a New Author Entry',
             'url': reverse('author-create')},
            {'name': 'Edit this Author Entry',
             'url': reverse('author-update', args=(pk,))},
            ]
        context['actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in ('created', 'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, ''))

        context['info_message'] = info_message
        return context

author_detail_view = AuthorDetailView.as_view()


#
# AuthorListView
#
class AuthorListView(LoginRequiredMixin,
                     ListView):
    template_name = 'books/author_list_view.html'
    model = Author
    paginate_by = 50

author_list_view = AuthorListView.as_view()


#
# PromotionCreateView
#
class PromotionCreateView(LoginRequiredMixin,
                          CollectionCreateUpdateViewMixin,
                          CreateView):
    template_name = 'books/promotion_create_view.html'
    form_class = PromotionForm
    model = Promotion

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?created=true'
        return url

promotion_create_view = PromotionCreateView.as_view()


#
# PromotionUpdateView
#
class PromotionUpdateView(LoginRequiredMixin,
                          CollectionCreateUpdateViewMixin,
                          UpdateView):
    template_name = 'books/promotion_create_view.html'
    formset_template_name = 'books/_keyvalue_view.html'
    form_class = PromotionForm
    model = Promotion

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?updated=true'
        return url

promotion_update_view = PromotionUpdateView.as_view()


#
# PromotionDetailView
#
class PromotionDetailView(LoginRequiredMixin,
                          CollectionDetailViewMixin,
                          DetailView):
    template_name = 'books/promotion_detail_view.html'
    model = Promotion

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(PromotionDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        promotion = kwargs.get('object')
        pk = promotion and promotion.id or 0
        actions = [
            {'name': 'Create a New Promotion Entry',
             'url': reverse('promotion-create')},
            {'name': 'Edit this Promotion Entry',
             'url': reverse('promotion-update', args=(pk,))},
            ]
        context['actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in ('created', 'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, ''))

        context['info_message'] = info_message
        return context

promotion_detail_view = PromotionDetailView.as_view()


#
# PromotionListView
#
class PromotionListView(LoginRequiredMixin,
                        ListView):
    template_name = 'books/promotion_list_view.html'
    model = Promotion
    paginate_by = 50

promotion_list_view = PromotionListView.as_view()
