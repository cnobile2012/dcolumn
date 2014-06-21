from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from dcolumn import settings


urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^parent/', include('dcolumn.dynamic_columns.urls')),
    )

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^dev/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_URL, 'show_indexes': True}),
        #url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        #    {'document_root': settings.MEDIA_ROOT}),
        )
else:
    urlpatterns += patterns(
        '',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_URL, 'show_indexes': True}),
        )
