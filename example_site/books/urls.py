#
# example_site/books/urls.py
#

from django.conf.urls import *


urlpatterns = patterns(
    'example_site.books.views',
    # Publisher
    url(r'^publisher-create/$', 'publisher_create_view',
        name='publisher-create'),
    url(r'^publisher-update/(?P<pk>\d+)/$', 'publisher_update_view',
        name='publisher-update'),
    url(r'^publisher-detail/(?P<pk>\d+)/$', 'publisher_detail_view',
        name='publisher-detail'),
    url(r'^publisher-list/$', 'publisher_list_view', name='publisher-list'),
    # Author
    url(r'^author-create/$', 'author_create_view',
        name='author-create'),
    url(r'^author-update/(?P<pk>\d+)/$', 'author_update_view',
        name='author-update'),
    url(r'^author-detail/(?P<pk>\d+)/$', 'author_detail_view',
        name='author-detail'),
    url(r'^author-list/$', 'author_list_view', name='author-list'),
    # Book
    url(r'^book-create/$', 'book_create_view',
        name='book-create'),
    url(r'^book-update/(?P<pk>\d+)/$', 'book_update_view',
        name='book-update'),
    url(r'^book-detail/(?P<pk>\d+)/$', 'book_detail_view',
        name='book-detail'),
    url(r'^book-list/$', 'book_list_view', name='book-list'),
    # Promotion
    url(r'^promotion-create/$', 'promotion_create_view',
        name='promotion-create'),
    url(r'^promotion-update/(?P<pk>\d+)/$', 'promotion_update_view',
        name='promotion-update'),
    url(r'^promotion-detail/(?P<pk>\d+)/$', 'promotion_detail_view',
        name='promotion-detail'),
    url(r'^promotion-list/$', 'promotion_list_view', name='promotion-list'),
    )
