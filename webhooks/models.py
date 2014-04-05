import logging

from django.conf import settings
from django.db import models, transaction
from django.dispatch.dispatcher import receiver


logger = logging.getLogger(__name__)


class Webhook(models.Model):
    """Represents a single Trello API webhook."""
    # something to remember this by, e.g. "Current board updates"
    name = models.CharField(
        max_length=50,
        help_text=u"A memorable name for the trigger event."
    )
    # the auth token
    token = models.CharField(
        max_length=50,
        help_text=u"The Trello API auth token."
    )

    def __unicode__(self):
        return u"Webhook: '%s' -> %s" % (self.name, self.get_callback_url())

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_callback_url(self):
        """Like get_absolute_url, but for the callbackURL required by Trello."""