import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Set the ContentType of all addAttachmentToCard CallbackEvents in the db"

    def handle(self, *args, **options):
    	"""
    	When a CallbackEvent is of type addAttachmentToCard, we automatically ping the URL of the attachment
    	to find out its content type.  This command will do this for all events of that type e.g. to cover any 
    	CallbackEvents created before the new feature.
    	"""
    	for ce in CallbackEvent.objects.filter(event_type='addAttachmentToCard'):
			ce.attachment_content_type = ce.discover_attachment_content_type()
			logger.info(u"CallbackEvent %s: '%s' has content type '%s'", ce.id, ce.attachment_url, ce.attachment_content_type)
			ce.save()