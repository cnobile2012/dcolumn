#
# example_site/books/urls.py
#

from django.conf.urls import *


urlpatterns = patterns(
    'example_site.books.views',
    url(r'create/$', 'book_create_view', name='book-create'),
    url(r'update/(?P<pk>\d+)/$', 'book_update_view', name='book-update'),
    url(r'detail/(?P<pk>\d+)/$', 'book_detail_view', name='book-detail'),
    )
