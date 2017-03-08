# # -*- coding: utf-8 -*-
# update existing attachment-events with contentType
import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update CallBackEvents with contentType in attachments' payload"

    def handle(self, *args, **options):
        """Updates the image field on addAttachmentToCard events
        """
        events_with_attachments = CallbackEvent.objects.filter(
            event_type="addAttachmentToCard")

        updated = 0
        logger.info(u"Started updating attachments with contentType. Total count: %s." % events_with_attachments.count())
        for event in events_with_attachments:
            if "contentType" not in event.action_data['attachment']:
                event.save(update_fields=['event_payload'])
                updated += 1

        logger.info(u"Finished updating attachments with contentType. Updated count: %s." % updated)
