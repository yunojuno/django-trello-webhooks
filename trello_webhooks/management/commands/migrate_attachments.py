# # -*- coding: utf-8 -*-
# sync webhooks down from Trello
import logging

from django.core.management.base import BaseCommand
from trello_webhooks.models import CallbackEvent

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Migrates call back attachment data structure to include attachment type."

    def handle(self, *args, **options):
        """Update existing 'addAttachmentToCard' callback events with attachment type.

        This command should be used to migrate from versions of the app which do not
        support storing attachment MIME type.

        """
        logger.info(u"Preparing to migrate 'addAttachmentToCard' callback events.")
        callback_events = CallbackEvent.objects.filter(event_type="addAttachmentToCard")
        logger.info(u"Found {0} 'addAttachmentToCard' callback events.".format(callback_events.count()))

        updated = 0

        for callback_event in callback_events:
            if "mainType" not in callback_event.action_data["attachment"]:
                # Save method will trigger addition of attachment type
                callback_event.save()
                updated += 1

        logger.info(u"Found {0} 'addAttachmentToCard' callback events requiring migration.".format(updated))
        logger.info(u"Completed migration.")