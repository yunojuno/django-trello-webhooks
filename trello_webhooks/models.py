# # -*- coding: utf-8 -*-
import json
import logging

from django.core.urlresolvers import reverse
from django.db import models
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import timezone

from jsonfield import JSONField
import trello

from trello_webhooks import settings
from trello_webhooks import signals

logger = logging.getLogger(__name__)


# free-floating function to get a new trello.TrelloClient object
# using the stored settings
def get_trello_client(api_key=settings.TRELLO_API_KEY,
                      api_secret=settings.TRELLO_API_SECRET,
                      token=None):  # noqa
    return trello.TrelloClient(api_key, api_secret=api_secret, token=token)


class TrelloWebhookManager(object):
    """Model manager used to interact with Trello API."""

    def __init__(self):
        self.client = get_trello_client()

    def list_hooks(self, auth_token):
        """Return all the hooks registered on Trello for a given auth_token.

        Args:
            auth_token: string, a valid user auth token, stored on a WebHook
                model as Webhook.auth_token

        """
        return self.client.list_hooks(token=auth_token)


class Webhook(models.Model):
    """Represents a single Trello API webhook."""
    trello_model_id = models.CharField(
        max_length=24,
        help_text=u"The id of the model being watched.",
    )
    trello_id = models.CharField(
        max_length=24,
        help_text=u"Webhook id returned from Trello API.",
        blank=True,
        # unique=True
    )
    # something to remember this by, e.g. "Current board updates"
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
    # mark whether active or not - linked to whether Trello knows what it is.
    is_active = models.NullBooleanField(default=None)
    created_at = models.DateTimeField(blank=True)
    last_updated_at = models.DateTimeField(blank=True)

    # this reflects the reality of the Trello API
    unique_together = ('trello_model_id', 'auth_token')

    remote_objects = TrelloWebhookManager()

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

    def get_absolute_url(self):
        """The callback_url used by Trello."""
        return reverse(
            'trello_callback_url',
            kwargs={
                'auth_token': self.auth_token,
                'trello_model_id': self.trello_model_id
            }
        )

    @property
    def has_trello_id(self):
        return self.trello_id != ''

    @property
    def callback_url(self):
        """The callback_url used by Trello."""
        return settings.CALLBACK_DOMAIN + self.get_absolute_url()

    @property
    def trello_url(self):
        """The API prefix used to call Trello."""
        return '/webhooks/%s' % self.trello_id

    def get_client(self):
        """Return a TrelloClient with the instance token."""
        assert self.auth_token != '', "Missing auth_token."
        return get_trello_client(token=self.auth_token)

    def post_args(self):
        """Return properties as dict using Trello property names."""
        return {
            'callbackURL': self.callback_url,
            'description': self.description,
            'idModel': self.trello_model_id,
        }

    def touch(self):
        """Update last_updated_at timestamp only."""
        self.last_updated_at = timezone.now()
        return super(Webhook, self).save(update_fields=['last_updated_at'])

    def save(self, *args, **kwargs):
        """Update timestamps, and sync with Trello on first save.

        If this is the first save (id=None), then we'll attempt to sync
        with Trello, unless the 'sync' kwarg is passed in and False.

        """
        # do not process side effects if we're doing a partial model update
        if kwargs.pop('sync', True):
            self.sync()
        self.last_updated_at = timezone.now()
        self.created_at = self.created_at or self.last_updated_at
        super(Webhook, self).save(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        """Delete the remote Trello webhook as well as the local instance."""
        # the underlying SQL row has been deleted, but the object still exists,
        # so we can still reference self.
        # https://docs.djangoproject.com/en/1.7/ref/models/instances/#django.db.models.Model.delete  # noqa
        if self.has_trello_id:
            self._delete_remote()
        super(Webhook, self).delete(*args, **kwargs)
        return self

    def _trello_sync(self, verb):
        """Calls Trello API, update from response JSON."""
        try:
            response = self.get_client().fetch_json(
                self.trello_url,
                http_method=verb,
                post_args=self.post_args()
            )
            self.trello_id = response.get('id', '')
            self.is_active = response.get('active', True) and self.has_trello_id
        except trello.ResourceUnavailable, ex:
            logger.warning(u"Error syncing webhook to trello: %s", ex)
            # if we get a 404 then clear out the Trello Id
            self.trello_id = '' if ex._status == 404 else self.trello_id
            self.is_active = False
        return self

    def _update_remote(self):
        """Update the remote Trello entity."""
        assert self.has_trello_id, "You cannot PUT to Trello without a trello_id."
        return self._trello_sync('PUT')

    def _create_remote(self):
        """Create a new remote Trello entity."""
        assert not self.has_trello_id, "You cannot POST to Trello with a trello_id."
        return self._trello_sync('POST')

    def _delete_remote(self):
        """Delete a new remote Trello entity."""
        assert self.has_trello_id, "You cannot DELETE from Trello without a trello_id."
        return self._trello_sync('DELETE')

    def sync(self):
        """Synchronise webhook with Trello.

        If the object has a trello_id then we assume it's valid, and send
        a PUT request to the API. If there is no trello_id then we assume
        that it's new, and POST it.

        Either call can fail - if we attempt to PUT to a trello_id that does
        not in fact exist, or we attempt to POST a combination of (auth_token,
        trello_model_id, callback_url) that already exists on Trello.

        Does not save the object, just updates the local trello_id property.
        Saving the local object is the calling code's responsibility.

        """
        if self.has_trello_id:
            # we have a Trello id, so PUT
            return self._update_remote()
        else:
            return self._create_remote()

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
            event_payload=body_text
        ).save()
        self.touch()
        signals.callback_received.send(sender=self.__class__, event=event)
        return event


class CallbackEvent(models.Model):
    """Model used to log all callbacks."""
    # ref to the webhook that picked up the event
    webhook = models.ForeignKey(Webhook)
    # events are read-only so just a timestamp required
    timestamp = models.DateTimeField()
    # the Trello event type - moveCard, commentCard, etc.
    event_type = models.CharField(max_length=50)
    # the complete request payload, as JSON
    event_payload = JSONField()

    def __unicode__(self):
        if self.id:
            return (
                "CallbackEvent %i: '%s' raised by webhook %s." %
                (self.id, self.event_type, self.webhook.id)
            )
        else:
            return (
                "CallbackEvent: '%s' raised by webhook %s." %
                (self.event_type, self.webhook.id)
            )

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return (
            u"<CallbackEvent id=%s, webhook=%s, event_type='%s'>" %
            (self.id, self.webhook_id, self.event_type)
        )

    def save(self, *args, **kwargs):
        """Update timestamp"""
        self.timestamp = timezone.now()
        super(CallbackEvent, self).save(*args, **kwargs)
        return self

    @property
    def action_data(self):
        """Returns the 'data' node from the payload."""
        return self.event_payload.get('action', {}).get('data')

    @property
    def member(self):
        """Returns 'memberCreator' JSON extracted from event_payload."""
        return self.event_payload.get('action', {}).get('memberCreator')

    @property
    def board(self):
        """Returns 'board' JSON extracted from event_payload."""
        return self.action_data.get('board') if self.action_data else None

    @property
    def list(self):
        """Returns 'list' JSON extracted from event_payload."""
        return self.action_data.get('list') if self.action_data else None

    @property
    def card(self):
        """Returns 'card' JSON extracted from event_payload."""
        return self.action_data.get('card') if self.action_data else None

    @property
    def member_name(self):
        """Return member name if it exists (used in admin)."""
        return self.member.get('fullName') if self.member else None

    @property
    def board_name(self):
        """Return board name if it exists (used in admin)."""
        return self.board.get('name') if self.board else None

    @property
    def list_name(self):
        """Return list name if it exists (used in admin)."""
        return self.list.get('name') if self.list else None

    @property
    def card_name(self):
        """Return card name if it exists (used in admin)."""
        return self.card.get('name') if self.card else None

    @property
    def template(self):
        """Return full path to render template, based on event_type."""
        return 'trello_webhooks/%s.html' % self.event_type

    def render(self):
        """Render the event using an HTML template.

        The path to the template comes from the `template` property,
        which is derived from the event_type.

        If the template does not exist (typically this would be because
        we capture a new event type that we haven't previously encountered),
        a warning is logged, and None is returned. (We return None instead
        of an empty string to make it clear that something has gone wrong -
        an empty string _could_ be a realistic output, if someone has
        overridden a template and spelled the context vars incorrectly.)

        The event_payload is passed in to the template as the context.

        Default templates exist for most event types, but you are encouraged
        to override these templates in your own project (see the template
        property for the full path to the template that is loaded).

        """
        try:
            return render_to_string(self.template, self.event_payload)
        except TemplateDoesNotExist:
            logger.warning(
                u"Missing or misconfigured template: '%s'",
                self.template
            )
            return None
