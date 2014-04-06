from django.conf.urls import patterns, url

from trello_webhooks import views

urlpatterns = patterns(views,
    url(
        r'^(?P<auth_token>\w+)/(?P<trello_model_id>\w+)/$',
        views.api_callback,
        name="trello_callback_url"
    ),
)
