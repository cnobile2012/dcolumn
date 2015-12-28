#
# example_site/books/urls.py
#

from django.conf.urls import *

from example_site.books import views


urlpatterns = [
    # Publisher
    url(r'^publisher-create/$', views.publisher_create_view,
        name='publisher-create'),
    url(r'^publisher-update/(?P<pk>\d+)/$', views.publisher_update_view,
        name='publisher-update'),
    url(r'^publisher-detail/(?P<pk>\d+)/$', views.publisher_detail_view,
        name='publisher-detail'),
    url(r'^publisher-list/$', views.publisher_list_view,
        name='publisher-list'),
    # Author
    url(r'^author-create/$', views.author_create_view,
        name='author-create'),
    url(r'^author-update/(?P<pk>\d+)/$', views.author_update_view,
        name='author-update'),
    url(r'^author-detail/(?P<pk>\d+)/$', views.author_detail_view,
        name='author-detail'),
    url(r'^author-list/$', views.author_list_view, name='author-list'),
    # Book
    url(r'^book-create/$', views.book_create_view,
        name='book-create'),
    url(r'^book-update/(?P<pk>\d+)/$', views.book_update_view,
        name='book-update'),
    url(r'^book-detail/(?P<pk>\d+)/$', views.book_detail_view,
        name='book-detail'),
    url(r'^book-list/$', views.book_list_view, name='book-list'),
    # Promotion
    url(r'^promotion-create/$', views.promotion_create_view,
        name='promotion-create'),
    url(r'^promotion-update/(?P<pk>\d+)/$', views.promotion_update_view,
        name='promotion-update'),
    url(r'^promotion-detail/(?P<pk>\d+)/$', views.promotion_detail_view,
        name='promotion-detail'),
    url(r'^promotion-list/$', views.promotion_list_view,
        name='promotion-list'),
    ]
