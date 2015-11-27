# # -*- coding: utf-8 -*-
# sync webhooks down from Trello
import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent


class Command(BaseCommand):
    help = "Update CallbackEvents with attachments to include an image field"

    def handle(self, *args, **options):
        """Updates the image field on addAttachmentToCard events
        """
        attachment_events = CallbackEvent.objects.filter(
            event_type="addAttachmentToCard")
        updated = 0

        for event in attachment_events:
            event.save()
            updated += 1

        print(u"Updated {0} 'addAttachmentToCard' events.".format(updated))
