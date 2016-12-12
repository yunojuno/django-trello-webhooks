# # -*- coding: utf-8 -*-
# sync webhooks down from Trello
import logging

from django.core.management.base import BaseCommand
from trello_webhooks.models import CallbackEvent

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = u"Sets contentType (if appropriate) for all `CallbackEvent`s"

    def handle(self, *args, **options):
        callback_events = list(CallbackEvent.objects.filter(event_type='addAttachmentToCard'))
        for ce in callback_events:
            ce.save()
        logger.info(u"Updated {} CallbackEvent instances".format(len(callback_events)))
