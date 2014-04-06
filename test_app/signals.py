# # -*- coding: utf-8 -*-
from django.dispatch import receiver

from trello_webhooks.signals import callback_received


@receiver(callback_received, dispatch_uid="callback_received")
def on_callback_received(sender, **kwargs):
    event = kwargs.pop('event')
    print "This is the event payload: ", event.event_payload
