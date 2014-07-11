#
# example_site/books/urls.py
#

from django.conf.urls import *


urlpatterns = patterns(
    'example_site.books.views',
    # Publisher
    url(r'publisher-create/$', 'publisher_create_view',
        name='publisher-create'),
    url(r'publisher-update/(?P<pk>\d+)/$', 'publisher_update_view',
        name='publisher-update'),
    url(r'publisher-detail/(?P<pk>\d+)/$', 'publisher_detail_view',
        name='publisher-detail'),
    # Author
    url(r'author-create/$', 'author_create_view',
        name='author-create'),
    url(r'author-update/(?P<pk>\d+)/$', 'author_update_view',
        name='author-update'),
    url(r'author-detail/(?P<pk>\d+)/$', 'author_detail_view',
        name='author-detail'),
    # Book
    url(r'create/$', 'book_create_view',
        name='book-create'),
    url(r'update/(?P<pk>\d+)/$', 'book_update_view',
        name='book-update'),
    url(r'detail/(?P<pk>\d+)/$', 'book_detail_view',
        name='book-detail'),
    )