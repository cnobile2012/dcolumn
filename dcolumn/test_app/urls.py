#
# dcolumn/test_app/urls.py
#

from django.urls import re_path, path

from . import views


urlpatterns = [
    path('test-book-create/', views.test_book_create_view,
         name='test-book-create'),
    re_path(r'^test-book-update/(?P<pk>\d+)/$', views.test_book_update_view,
        name='test-book-update'),
    re_path(r'^test-book-detail/(?P<pk>\d+)/$', views.test_book_detail_view,
        name='test-book-detail'),
    path('test-book-list/', views.test_book_list_view,
         name='test-book-list'),
    ]
