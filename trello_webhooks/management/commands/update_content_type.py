# # -*- coding: utf-8 -*-
# Populate missing mimetypes on CallbackEvent attachments
import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Try to populate any missing event attachment mimetypes."

    def handle(self, *args, **options):
        events = CallbackEvent.objects.filter(event_type="addAttachmentToCard")
        event_count = events.count()
        logger.info("Processing %d events..." % event_count)
        for event in events:
            event.save()
        logger.info("Done.")
