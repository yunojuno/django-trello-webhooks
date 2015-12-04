# # -*- coding: utf-8 -*-
from django.db import models


class EventType(models.Model):

    """Canonical list of Trello events."""

    label = models.CharField(
        max_length=30,
        help_text="The name of the event as sent from Trello."
    )
    event_count = models.IntegerField(
        default=0,
        help_text="The count of times this event has been received - "
                  "ignores the is_active attr."
    )
    is_active = models.BooleanField(
        default=True,
        help_text=u"If True, send notification to HipChat, else ignore."
    )
