# # -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.dispatch import receiver

from trello_webhooks.signals import callback_received

from test_app.hipchat import send_to_hipchat

logger = logging.getLogger(__name__)


@receiver(callback_received, dispatch_uid="callback_received")
def on_callback_received(sender, **kwargs):
    event = kwargs.pop('event')
    if settings.HIPCHAT_ENABLED:
        send_to_hipchat(event.render())
