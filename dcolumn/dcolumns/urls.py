#
# dcolumn/dcolumns/urls.py
#

from django.conf.urls import *


urlpatterns = patterns(
    'dcolumn.dcolumns.views',
    url(r'api/collections/', 'collection_ajax_view', name="api-collections"),
    )
