#
# dcolumn/dcolumns/urls.py
#

"""
URLs used in DColumns.

re_path(r'api/collections/(?P<class_name>\w+)/$', collection_ajax_view,
        name="api-collections")
"""
__docformat__ = "restructuredtext en"

from django.urls import include, re_path, path
from .views import collection_ajax_view

app_name = 'dcolumns'
urlpatterns = [
    re_path(r'api/collections/(?P<class_name>\w+)/$', collection_ajax_view,
            name="api-collections"),
    ]
