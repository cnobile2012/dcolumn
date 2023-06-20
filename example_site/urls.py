from django.urls import include, re_path, path
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.views.static import serve

from .settings import DEBUG, TRAVIS, STATIC_URL

admin.autodiscover()
admin.site.site_header = "Books Admin"

urlpatterns = [
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^book/', include('example_site.books.urls')),
    re_path(r'^dcolumns/', include('dcolumn.dcolumns.urls')),
    re_path(r'^$', TemplateView.as_view(template_name='home.html'),
            name='home'),
    ]

if DEBUG:
    import debug_toolbar

    urlpatterns += [
        re_path(r'^dev/(?P<path>.*)$', serve,
                {'document_root': STATIC_URL, 'show_indexes': True}),
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
        re_path(r'^tests/', include('dcolumn.test_app.urls'))
        ]
elif TRAVIS:
    urlpatterns += [
        re_path(r'^tests/', include('dcolumn.test_app.urls'))
        ]
else:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve,
                {'document_root': STATIC_URL, 'show_indexes': True}),
        ]
