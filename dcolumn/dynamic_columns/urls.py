#
# dcolumn/dynamic_columns/urls.py
#

from django.conf.urls import *


urlpatterns = patterns(
    'dcolumn.dynamic_columns.views',
    url(r'api/dynamic-column/', 'dynamic_column_ajax_view',
        name="api-dynamic-column"),
    url(r'create/$', 'parent_create_view',
        name='parent-create'),
    url(r'update/(?P<pk>\d+)/$', 'parent_update_view',
        name='parent-update'),
    url(r'detail/(?P<pk>\d+)/$', 'parent_detail_view',
        name='parent-detail'),
    )
