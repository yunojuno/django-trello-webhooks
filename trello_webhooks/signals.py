# # -*- coding: utf-8 -*-
# trello_webhooks.signals
from django.dispatch import Signal

# The callback_received signal is fired when a webhook is called by Trello.
# event: a CallbackEvent object, containing the event payload (as JSON)
callback_received = Signal(providing_args=['event'])
