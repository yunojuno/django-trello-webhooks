from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'welcome/$', TemplateView.as_view(template_name='welcome.html')),
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^webhooks/',
        include('trello_webhooks.urls')
    ),
)
