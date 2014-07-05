#
# dcolumn/dcolumns/urls.py
#

from django.conf.urls import *


urlpatterns = patterns(
    'dcolumn.dcolumns.views',
    url(r'api/collections/(?P<class_name>\w+)/$', 'collection_ajax_view',
        name="api-collections"),
    )
