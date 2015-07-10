import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Add attachment content type to callback event payload."

    def handle(self, *args, **options):
        callback_events = CallbackEvent.objects.filter(event_type='addAttachmentToCard')
        for ce in callback_events:
            ce.save()
            logger.info(u"Added content type to %r", ce)
        logger.info(u"Content type added to %d callback events.", callback_events.count())
