#
# example_site/books/urls.py
#

try:
    from django.urls import re_path
except:
    from django.conf.urls import url as re_path

from example_site.books import views


urlpatterns = [
    # Publisher
    re_path(r'^publisher-create/$', views.publisher_create_view,
        name='publisher-create'),
    re_path(r'^publisher-update/(?P<pk>\d+)/$', views.publisher_update_view,
        name='publisher-update'),
    re_path(r'^publisher-detail/(?P<pk>\d+)/$', views.publisher_detail_view,
        name='publisher-detail'),
    re_path(r'^publisher-list/$', views.publisher_list_view,
        name='publisher-list'),
    # Author
    re_path(r'^author-create/$', views.author_create_view,
        name='author-create'),
    re_path(r'^author-update/(?P<pk>\d+)/$', views.author_update_view,
        name='author-update'),
    re_path(r'^author-detail/(?P<pk>\d+)/$', views.author_detail_view,
        name='author-detail'),
    re_path(r'^author-list/$', views.author_list_view, name='author-list'),
    # Book
    re_path(r'^book-create/$', views.book_create_view, name='book-create'),
    re_path(r'^book-update/(?P<pk>\d+)/$', views.book_update_view,
        name='book-update'),
    re_path(r'^book-detail/(?P<pk>\d+)/$', views.book_detail_view,
        name='book-detail'),
    re_path(r'^book-list/$', views.book_list_view, name='book-list'),
    # Promotion
    re_path(r'^promotion-create/$', views.promotion_create_view,
        name='promotion-create'),
    re_path(r'^promotion-update/(?P<pk>\d+)/$', views.promotion_update_view,
        name='promotion-update'),
    re_path(r'^promotion-detail/(?P<pk>\d+)/$', views.promotion_detail_view,
        name='promotion-detail'),
    re_path(r'^promotion-list/$', views.promotion_list_view,
        name='promotion-list'),
    ]
