# # -*- coding: utf-8 -*-
import functools
import json
import logging

from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone

import trello

from trello_webhooks import settings, signals

logger = logging.getLogger(__name__)

# this provides simple access to the underlying trello.TrelloClient
# class, without having to pass in the settings all the time.
TrelloClient = functools.partial(
    trello.TrelloClient,
    settings.TRELLO_API_KEY,
    settings.TRELLO_API_SECRET
)


class Webhook(models.Model):
    """Represents a single Trello API webhook."""
    # something to remember this by, e.g. "Current board updates"
    trello_model_id = models.CharField(
        max_length=24,
        help_text=u"The id of the model being watched.",
    )
    trello_id = models.CharField(
        max_length=24,
        help_text=u"Webhook id returned from Trello API.",
        blank=True,
    )
    description = models.CharField(
        max_length=500,
        help_text=u"Description of the webhook.",
        blank=True
    )
    # the auth token
    auth_token = models.CharField(
        max_length=64,
        help_text=u"The Trello API user auth token."
    )
    created_at = models.DateTimeField(blank=True)
    last_updated_at = models.DateTimeField(blank=True)

    # this reflects the reality of the Trello API
    unique_together = ('trello_model_id', 'auth_token')

    @property
    def has_trello_id(self):
        return self.trello_id != ''

    @property
    def callback_url(self):
        """The callback_url used by Trello."""
        return settings.CALLBACK_DOMAIN + self.get_absolute_url()

    def _client(self):
        """Creates a TrelloClient from the instance token and app settings."""
        assert self.auth_token != '', "Missing auth_token"
        return TrelloClient(token=self.auth_token)

    def get_absolute_url(self):
        """The callback_url used by Trello."""
        return reverse(
            'trello_callback_url',
            kwargs={
                'auth_token': self.auth_token,
                'trello_model_id': self.trello_model_id
            }
        )

    def __unicode__(self):
        if self.id:
            return u"Webhook %i: %s" % (self.id, self.callback_url)
        else:
            return u"Webhook: %s" % (self.callback_url)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return (
            u"<Webhook id=%s, trello_id='%s', model='%s'>" %
            (self.id, self.trello_id, self.trello_model_id)
        )

    def save(self, *args, **kwargs):
        """Update timestamps, and sync with Trello on first save.

        If this is the first save (id=None), then we'll attempt to sync
        with Trello, unless the 'sync' kwarg is passed in and False.

        """
        if self.id is None and kwargs.pop('sync', True):
            logger.debug(u"New Webhook (%r) - syncing with Trello", self)
            self.sync(save=False)
        self.last_updated_at = timezone.now()
        self.created_at = self.created_at or self.last_updated_at
        super(Webhook, self).save(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        """Delete the remote Trello webhook as well as the local instance."""
        super(Webhook, self).delete(*args, **kwargs)
        # the underlying SQL row has been deleted, but the object still exists,
        # so we can still reference self.
        # https://docs.djangoproject.com/en/1.7/ref/models/instances/#django.db.models.Model.delete  # noqa
        if self.has_trello_id:
            try:
                # don't bother checking, just power on through
                self._fetch().delete()
                logger.debug(u"%r removed from Trello", self)
            except AttributeError:
                logger.warning(u"Unable to delete %r from Trello.", self)

    def _fetch(self):
        """Fetches the corresponding webhook from Trello API.

        Returns a py-trello WebHook instance if one is found that matches,
            else None.

        """
        for hook in self._client().list_hooks():
            if hook.id_model == self.trello_model_id:
                logger.debug(u"Found matching Trello webhook registered for %s", self.trello_model_id)  # noqa
                return hook
        logger.debug(u"No matching Trello webhook registered for %s", self.trello_model_id)
        return None

    def _pull(self):
        """Fetch remote webhook and 'pull' it into local copy.

        This method calls `_fetch` to get the remote webhook (if it exists),
        and then pulls the Trello id into the instance.

        If the existing description field is blank, and the remote one is not
        then it will also update the description.

        If no matching webhook is found, the local trello_id is cleared out -
        this can be used to check whether a match was found.

        Returns the updated object (unsaved)

        """
        hook = self._fetch()
        if hook is None:
            self.trello_id = ''
        else:
            self.trello_id = hook.id
            if self.description == "":
                self.description = hook.desc
        return self

    def _push(self):
        """Push local webhook to Trello.

        This is a companion function to _pull, and is used to register a
        new webhook with Trello. The local trello_id will be updated with
        the new id if it is created.

        NB This will poke Trello to immediately respond with a callback.

        Returns the updated object (unsaved)

        """
        hook = self._client().create_hook(
            callback_url=self.callback_url,
            id_model=self.trello_model_id,
            desc=self.description
        )
        if hook is False:
            self.trello_id = ''
            logger.debug(u"Webhook (%r) deactivated as Trello API returned False.", self)
        else:
            self.trello_id = hook.id
            logger.debug(u"Webhook (%r) registered successfuly with Trello API.", self)
        return self

    def _touch(self):
        """Update last_updated_at timestamp."""
        self.last_updated_at = timezone.now()
        return self.save(update_fields=['last_updated_at'])

    def sync(self, save=True):
        """Synchronise webhook with Trello.

        Calls _pull to see if there is an existing remote webhook, and
        if not calls _push to create one. Saves the updated object (will
        now have trello_id set).

        Kwargs:
            save: boolean (True), if False then do not save the object - useful
                when called from within a save-related method / signal receiver.

        Returns the updated instance

        """
        self._pull()
        if not self.has_trello_id:
            self._push()
        if save is True:
            self.save()
        return self

    def add_callback(self, body_text):
        """Add a new CallbackEvent instance and fire signal.

        This is called from the callback view, with the JSON body. It
        creates a new CallbackEvent.

        Returns the new CallbackEvent instance.

        """
        payload = json.loads(body_text)
        action = payload['action']['type']
        event = CallbackEvent(
            webhook=self,
            event_type=action,
            event_payload=payload
        ).save()
        self._touch()
        signals.callback_received.send(sender=self.__class__, event=event)
        return event


class CallbackEvent(models.Model):
    """Model used to log all callbacks."""
    # ref to the webhook that picked up the event
    webhook = models.ForeignKey(Webhook)
    timestamp = models.DateTimeField()
    # the Trello event type - moveCard, commentCard, etc.
    event_type = models.CharField(max_length=50)
    # the complete request payload, as JSON
    event_payload = models.TextField()

    def save(self, *args, **kwargs):
        """Update timestamp"""
        self.timestamp = timezone.now()
        super(CallbackEvent, self).save(*args, **kwargs)
        return self
