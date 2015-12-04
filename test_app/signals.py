# # -*- coding: utf-8 -*-
import logging
from os import path, listdir

from django.conf import settings
from django.dispatch import receiver

from trello_webhooks.signals import callback_received

from test_app.hipchat import send_to_hipchat
from test_app.models import EventType

logger = logging.getLogger(__name__)


def get_supported_events():
    """Returns the list of available _local_ templates.

    If a template exists in the local app, it will take precedence
    over the default trello_webhooks template. The base assumption
    for this function is that _if_ a local template exists, then this
    is an event we are interested in.

    """
    app_template_path = path.join(
        path.realpath(path.dirname(__file__)),
        'templates/trello_webhooks'
    )
    return [t.split('.')[0] for t in listdir(app_template_path)]


def record_event(event_type):
    """Lookup the EventType, increment the count."""
    try:
        et = EventType.objects.get(label=event_type)
    except EventType.DoesNotExist:
        et = EventType.objects.create(label=event_type)
    et.event_count += 1
    et.save()
    return et


@receiver(callback_received, dispatch_uid="callback_received")
def on_callback_received(sender, **kwargs):
    # if a template exists for the event_type, then send the output
    # as a normal notification, in 'yellow'
    # if no template exists, send a notification in 'red'
    event = kwargs.pop('event')
    event_type = record_event(event.event_type)
    if not event_type.is_active:
        logger.debug(u"Suppressing inactive Trello event '%s'", event_type.label)
        return
    html = event.render()
    if settings.HIPCHAT_ENABLED:
        logger.debug(
            u"Message sent to HipChat [%s]: %r",
            send_to_hipchat(html), event, event.webhook
        )
    else:
        logger.debug(
            u"HipChat is DISABLED, logging message instead: '%s'",
            html
        )
