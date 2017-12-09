from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.views.static import serve

from .settings import DEBUG, STATIC_URL

admin.autodiscover()
admin.site.site_header = "Books Admin"

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^book/', include('example_site.books.urls')),
    url(r'^dcolumns/', include('dcolumn.dcolumns.urls')),
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    ]

if DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^dev/(?P<path>.*)$', serve,
            {'document_root': STATIC_URL, 'show_indexes': True}),
        url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
else:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve,
            {'document_root': STATIC_URL, 'show_indexes': True}),
        ]
