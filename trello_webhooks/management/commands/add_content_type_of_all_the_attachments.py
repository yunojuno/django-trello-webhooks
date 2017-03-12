import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import CallbackEvent

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """
    	Adds content type of the attachments to all historic callback events.
    	"""

    def handle(self, *args, **options):

        callback_events = CallbackEvent.objects.filter(event_type='addAttachmentToCard')

        if not callback_events:
        	logger.warning("No CallbackEvent found for adding attachment content type")

        try:
	        for event in callback_events:
	            event.save()
	        logger.info("Content types for attachments added successfully")
	    except Exception as e:
	    	# Very generic exception handling as we're wrapping (or may be) lots of behaviour on callback event save 
	    	logger.error("Error on adding content type of attachment for event {}. Error:{}".format(event.id, e))