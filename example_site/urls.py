from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from .settings import DEBUG, STATIC_URL


urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^parent/', include('example_site.books.urls')),
    url(r'^dcolumns/', include('dcolumn.dcolumns.urls')),
    )

if DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^dev/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': STATIC_URL, 'show_indexes': True}),
        )
else:
    urlpatterns += patterns(
        '',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': STATIC_URL, 'show_indexes': True}),
        )
