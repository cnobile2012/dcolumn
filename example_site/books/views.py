#
# example_site/books/views.py
#

import logging

from django.views.generic import DetailView, CreateView, UpdateView, ListView
from django.core.urlresolvers import reverse

from dcolumn.dcolumns.views import (
    CollectionCreateUpdateViewMixin, CollectionDetailViewMixin)

from .models import Book, Publisher, Author, Promotion
from .forms import BookForm, PublisherForm, AuthorForm, PromotionForm

log = logging.getLogger('example_site.views')


#
# BookCreateView
#
class BookCreateView(CollectionCreateUpdateViewMixin, CreateView):
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
class BookUpdateView(CollectionCreateUpdateViewMixin, UpdateView):
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
class BookDetailView(CollectionDetailViewMixin, DetailView):
    template_name = u'books/book_detail_view.html'
    model = Book

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(BookDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        book = kwargs.get(u'object')
        pk = book and book.id or 0
        actions = [
            {u'name': u'Create a New Book Entry',
             u'url': reverse(u'book-create')},
            {u'name': u'Edit this Book Entry',
             u'url': reverse(u'book-update', args=(pk,))},
            ]
        context[u'actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in (u'created', u'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, u''))

        context[u'info_message'] = info_message
        return context

book_detail_view = BookDetailView.as_view()


#
# BookListView
#
class BookListView(ListView):
    template_name = u'books/book_list_view.html'
    model = Book
    paginate_by = 50

book_list_view = BookListView.as_view()


#
# PublisherCreateView
#
class PublisherCreateView(CollectionCreateUpdateViewMixin, CreateView):
    template_name = u'books/publisher_create_view.html'
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
class PublisherUpdateView(CollectionCreateUpdateViewMixin, UpdateView):
    template_name = u'books/publisher_create_view.html'
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
class PublisherDetailView(CollectionDetailViewMixin, DetailView):
    template_name = u'books/publisher_detail_view.html'
    model = Publisher

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(PublisherDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        publisher = kwargs.get(u'object')
        pk = publisher and publisher.id or 0
        actions = [
            {u'name': u'Create a New Publisher Entry',
             u'url': reverse(u'publisher-create')},
            {u'name': u'Edit this Publisher Entry',
             u'url': reverse(u'publisher-update', args=(pk,))},
            ]
        context[u'actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in (u'created', u'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, u''))

        context[u'info_message'] = info_message
        return context

publisher_detail_view = PublisherDetailView.as_view()


#
# PublisherListView
#
class PublisherListView(ListView):
    template_name = u'books/publisher_list_view.html'
    model = Publisher
    paginate_by = 50

publisher_list_view = PublisherListView.as_view()


#
# AuthorCreateView
#
class AuthorCreateView(CollectionCreateUpdateViewMixin, CreateView):
    template_name = u'books/author_create_view.html'
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
class AuthorUpdateView(CollectionCreateUpdateViewMixin, UpdateView):
    template_name = u'books/author_create_view.html'
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
class AuthorDetailView(CollectionDetailViewMixin, DetailView):
    template_name = u'books/author_detail_view.html'
    model = Author

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        author = kwargs.get(u'object')
        pk = author and author.id or 0
        actions = [
            {u'name': u'Create a New Author Entry',
             u'url': reverse(u'author-create')},
            {u'name': u'Edit this Author Entry',
             u'url': reverse(u'author-update', args=(pk,))},
            ]
        context[u'actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in (u'created', u'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, u''))

        context[u'info_message'] = info_message
        return context

author_detail_view = AuthorDetailView.as_view()


#
# AuthorListView
#
class AuthorListView(ListView):
    template_name = u'books/author_list_view.html'
    model = Author
    paginate_by = 50

author_list_view = AuthorListView.as_view()


#
# PromotionCreateView
#
class PromotionCreateView(CreateView):
    template_name = u'books/promotion_create_view.html'
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
class PromotionUpdateView(UpdateView):
    template_name = u'books/promotion_create_view.html'
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
class PromotionDetailView(DetailView):
    template_name = u'books/promotion_detail_view.html'
    model = Promotion

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        context = super(PromotionDetailView, self).get_context_data(**kwargs)
        # Create actions if any.
        promotion = kwargs.get(u'object')
        pk = promotion and promotion.id or 0
        actions = [
            {u'name': u'Create a New Promotion Entry',
             u'url': reverse(u'promotion-create')},
            {u'name': u'Edit this Promotion Entry',
             u'url': reverse(u'promotion-update', args=(pk,))},
            ]
        context[u'actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in (u'created', u'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, u''))

        context[u'info_message'] = info_message
        return context

promotion_detail_view = PromotionDetailView.as_view()


#
# PromotionListView
#
class PromotionListView(ListView):
    template_name = u'books/promotion_list_view.html'
    model = Promotion
    paginate_by = 50

promotion_list_view = PromotionListView.as_view()
