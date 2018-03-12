#
# dcolumn/dcolumns/tests/urls.py
#

try:
    from django.urls import re_path
except:
    from django.conf.urls import url as re_path

from . import views


urlpatterns = [
    re_path(r'^test-book-create/$', views.test_book_create_view,
        name='test-book-create'),
    re_path(r'^test-book-update/(?P<pk>\d+)/$', views.test_book_update_view,
        name='test-book-update'),
    re_path(r'^test-book-detail/(?P<pk>\d+)/$', views.test_book_detail_view,
        name='test-book-detail'),
    re_path(r'^test-book-list/$', views.test_book_list_view,
        name='test-book-list'),
    ]
