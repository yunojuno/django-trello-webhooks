from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^webhooks/', include('trello_webhooks.urls')),
)

if settings.DEBUG is False:
    urlpatterns += patterns(
        '',
        url(
            r'^static/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}
        ),
    )
