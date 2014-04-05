from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(
        r'callbacks/(?P<webhook_id>\d+)/$',
        'webhooks.views.api_callback',
        name="webhook_callback"
    ),
)
