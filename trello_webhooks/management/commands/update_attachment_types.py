# # -*- coding: utf-8 -*-
# retrospectively update the attachment 'type' attribute for
# relevant CallbackEvents in the DB
import logging

from django.core.management.base import BaseCommand, CommandError

from trello_webhooks.models import CallbackEvent

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Retrospectively adds attachment type data where possible'

    def handle(self, *args, **options):
        """

        """
        try:
            qs = CallbackEvent.objects.all()
        except CallbackEvent.DoesNotExist:
            raise CommandError('CallbackEvent "%s" does not exist' % poll_id)

        for event in qs:
            event.save()

        logger.info(u"Successfully added type field to all attachment data")