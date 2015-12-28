#
# dcolumn/dcolumns/urls.py
#

from django.conf.urls import *
from .views import collection_ajax_view


urlpatterns = [
    url(r'api/collections/(?P<class_name>\w+)/$', collection_ajax_view,
        name="api-collections"),
    ]
