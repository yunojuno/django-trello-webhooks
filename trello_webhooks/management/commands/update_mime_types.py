import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Add attachment types to CallbackEvents retroactively."

    def handle(self, *args, **options):
        logger.info('Starting the update of attachment types...')
        callbacks = CallbackEvent.objects.filter(event_type="addAttachmentToCard")
        for callback in callbacks:
            callback.save()
        logger.info('Updating CallbackEvent attachment types finished.')
