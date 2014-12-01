# # -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.dispatch import receiver

from trello_webhooks.signals import callback_received

from test_app.hipchat import send_to_hipchat

logger = logging.getLogger(__name__)


@receiver(callback_received, dispatch_uid="callback_received")
def on_callback_received(sender, **kwargs):
    # if a template exists for the event_type, then send the output
    # as a normal notification, in 'yellow'
    # if no template exists, send a notification in 'red'
    event = kwargs.pop('event')
    if settings.HIPCHAT_ENABLED:
        rendered = event.render()
        color = "yellow" if rendered else "red"
        html = rendered or (
            u"No template available for '%s'"
            % event.event_type
        )
        send_to_hipchat(html, color=color)
