from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.static import serve

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^webhooks/', include('trello_webhooks.urls')),
]

if settings.DEBUG is False:
    urlpatterns += [
        url(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': settings.STATIC_ROOT}
        ),
    ]
