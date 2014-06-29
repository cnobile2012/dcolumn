#
# example_site/books/urls.py
#

from django.conf.urls import *


urlpatterns = patterns(
    'example_site.books.views',
    url(r'create/$', 'parent_create_view',
        name='parent-create'),
    url(r'update/(?P<pk>\d+)/$', 'parent_update_view',
        name='parent-update'),
    url(r'detail/(?P<pk>\d+)/$', 'parent_detail_view',
        name='parent-detail'),
    )
