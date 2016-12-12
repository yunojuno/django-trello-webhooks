# # -*- coding: utf-8 -*-
# sync webhooks down from Trello
import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch content type of attachments when it's not present."

    def handle(self, *args, **options):
        """
        Go through all CallbackEvents of type 'addAttachmentToCard'
        and resave them, whether they haven't got an 'attachment.mimeType'
        field.

        """
        events = CallbackEvent.filter(event_type='addAttachmentToCard')
        for e in events:
            if not e.action_data.get('attachment', {}).get('mimeType'):
                e.save()
