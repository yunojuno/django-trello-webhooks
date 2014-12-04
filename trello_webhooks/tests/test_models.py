# -*- coding: utf-8 -*-
import datetime
import json
import mock

from django.core.urlresolvers import reverse
from django.test import TestCase

import trello

from trello_webhooks.models import Webhook, CallbackEvent
from trello_webhooks.settings import (
    TRELLO_API_KEY,
    TRELLO_API_SECRET,
    CALLBACK_DOMAIN
)
from trello_webhooks.tests import get_sample_data


def mock_trello_sync(webhook, verb):
    """Fake version of the Webhook._trello_sync method.

    This mock requires no direct connection to Trello, and is deterministic,
    so that it can be used in testing.

    It monkey-patches the Webhook object with the 'verb' kwarg, so that you
    can validate that the expected method was called.

    In addition it sets the trello_id property as per the real version.

    """
    webhook.verb = verb
    if verb == 'POST':
        webhook.trello_id = 'NEW_TRELLO_ID'
        webhook.is_active = True
    elif verb == 'DELETE':
        webhook.trello_id = ''
        webhook.is_active = False
    return webhook


def mock_trello_sync_x(webhook, verb):
    """Fake version of the Webhook._trello_sync method that mimics failure.

    This function mimics the result of _trello_sync if Trello responds with
    something other than a 200.

    """
    webhook = mock_trello_sync(webhook, verb)
    webhook.trello_id = ''
    webhook.is_active = False
    return webhook


class WebhookModelTests(TestCase):

    def test_default_properties(self):
        hook = Webhook()
        self.assertEqual(hook.id, None)
        self.assertEqual(hook.trello_model_id, '')
        self.assertEqual(hook.trello_id, '')
        self.assertEqual(hook.description, '')
        self.assertEqual(hook.created_at, None)
        self.assertEqual(hook.last_updated_at, None)
        self.assertEqual(hook.auth_token, '')
        self.assertIsNone(hook.is_active)

    def test_str_repr(self):
        hook = Webhook(trello_id='A', trello_model_id='B', auth_token='C')
        self.assertEqual(
            str(hook),
            u"Webhook: %s" % (hook.callback_url)
        )
        self.assertEqual(
            unicode(hook),
            u"Webhook: %s" % (hook.callback_url)
        )
        self.assertEqual(
            repr(hook),
            u"<Webhook id=%s, trello_id='%s', model='%s'>" %
            (hook.id, hook.trello_id, hook.trello_model_id)
        )
        # now with an id
        hook.id = 1
        self.assertEqual(
            str(hook),
            u"Webhook %i: %s" % (hook.id, hook.callback_url)
        )
        self.assertEqual(
            unicode(hook),
            u"Webhook %i: %s" % (hook.id, hook.callback_url)
        )
        self.assertEqual(
            repr(hook),
            u"<Webhook id=%s, trello_id='%s', model='%s'>" %
            (hook.id, hook.trello_id, hook.trello_model_id)
        )

    def test_get_absolute_url(self):
        hook = Webhook(
            trello_model_id="M",
            auth_token="A",
        ).save(sync=False)
        self.assertEqual(
            hook.get_absolute_url(),
            reverse(
                'trello_callback_url',
                kwargs={
                    'auth_token': hook.auth_token,
                    'trello_model_id': hook.trello_model_id
                }
            )
        )

    def test_has_trello_id(self):
        hook = Webhook()
        self.assertEqual(hook.trello_id, '')
        self.assertFalse(hook.has_trello_id)
        hook.trello_id = '1'
        self.assertTrue(hook.has_trello_id)

    def test_callback_url(self):
        hook = Webhook(
            trello_model_id="M",
            auth_token="A",
        ).save(sync=False)
        self.assertEqual(
            hook.callback_url,
            CALLBACK_DOMAIN + hook.get_absolute_url()
        )

    def test_trello_url(self):
        w = Webhook()
        self.assertEqual(w.trello_url, '/webhooks/')
        w.id = 1
        self.assertEqual(w.trello_url, '/webhooks/')
        w.id = None
        self.assertEqual(w.trello_url, '/webhooks/')

    def test_get_client(self):
        # should fail without a token
        w = Webhook()
        self.assertRaises(AssertionError, w.get_client)
        # give it a token and should now get back a TrelloClient
        w.auth_token = 'X'
        client = w.get_client()
        self.assertEqual(client.api_key, TRELLO_API_KEY)
        self.assertEqual(client.api_secret, TRELLO_API_SECRET)
        self.assertEqual(client.resource_owner_key, w.auth_token)
        self.assertEqual(client.resource_owner_secret, None)

    def test_post_args(self):
        w = Webhook(
            auth_token="X",
            description="Foo-Bar",
            trello_model_id="123"
        )
        self.assertEqual(
            w.post_args(),
            {
                'callbackURL': w.callback_url,
                'description': w.description,
                'idModel': w.trello_model_id
            }
        )

    def test_touch(self):
        hook = Webhook().save(sync=False)
        self.assertTrue(hook.created_at == hook.last_updated_at)
        hook.touch()
        self.assertTrue(hook.last_updated_at > hook.created_at)

    def test_save_no_sync(self):
        # Check that save updates the timestamps
        self.assertEqual(Webhook.objects.count(), 0)
        hook = Webhook().save(sync=False)
        self.assertEqual(Webhook.objects.count(), 1)
        self.assertIsNotNone(hook.id)
        self.assertEqual(hook.trello_model_id, '')
        self.assertEqual(hook.trello_id, '')
        self.assertEqual(hook.description, '')
        self.assertIsInstance(hook.created_at, datetime.datetime)
        self.assertEqual(hook.last_updated_at, hook.last_updated_at)
        self.assertEqual(hook.auth_token, '')
        timestamp = hook.created_at
        # and that saving again updates the last_updated_at
        hook.save(sync=False)
        self.assertEqual(hook.created_at, timestamp)
        self.assertNotEqual(hook.last_updated_at, timestamp)

    @mock.patch('trello_webhooks.models.Webhook._trello_sync', mock_trello_sync)
    def test_save_sync(self):
        # now try without syncing - should have no verb
        hook = Webhook()
        self.assertFalse(hasattr(hook, 'verb'))
        hook.save()
        self.assertEqual(hook.verb, 'POST')
        self.assertEqual(hook.trello_id, 'NEW_TRELLO_ID')
        # validate that an existing id is unchanged,
        hook.trello_id = 'OLD_TRELLO_ID'
        hook.save()
        self.assertEqual(hook.verb, 'PUT')
        self.assertEqual(hook.trello_id, 'OLD_TRELLO_ID')

    def test_delete(self):
        self.assertEqual(Webhook.objects.count(), 0)
        hook = Webhook().save(sync=False)
        self.assertEqual(Webhook.objects.count(), 1)
        hook.delete()
        self.assertEqual(Webhook.objects.count(), 0)

    @mock.patch('trello_webhooks.models.Webhook._trello_sync', mock_trello_sync)
    def test__update_remote(self):
        w = Webhook()
        # no trello_id, no update
        self.assertRaises(AssertionError, w._update_remote)
        w.trello_id = "123"
        w._update_remote()
        self.assertEqual(w.verb, 'PUT')

    @mock.patch('trello_webhooks.models.Webhook._trello_sync', mock_trello_sync)
    def test__create_remote(self):
        w = Webhook()
        w._create_remote()
        self.assertTrue(w.is_active)
        self.assertEqual(w.verb, 'POST')
        self.assertEqual(w.trello_id, 'NEW_TRELLO_ID')
        w.trello_id = "123"
        self.assertRaises(AssertionError, w._create_remote)

    @mock.patch('trello_webhooks.models.Webhook._trello_sync', mock_trello_sync)
    def test__delete_remote(self):
        w = Webhook()
        # no trello_id, no update
        self.assertRaises(AssertionError, w._delete_remote)
        w.trello_id = "123"
        w._delete_remote()
        self.assertEqual(w.verb, 'DELETE')
        self.assertEqual(w.trello_id, '')

    @mock.patch('trello_webhooks.models.Webhook._trello_sync', mock_trello_sync)
    def test_sync(self):
        w = Webhook()
        self.assertEqual(w.sync().verb, 'POST')
        w.trello_id = "123"
        self.assertEqual(w.sync().verb, 'PUT')

    def test_add_callback(self):
        hook = Webhook().save(sync=False)
        payload = get_sample_data('commentCard', 'json')
        event = hook.add_callback(json.dumps(payload))
        self.assertEqual(event.webhook, hook)
        self.assertEqual(event.event_payload, payload)
        # other CallbackEvent properties are tested in CallbackEvent tests


class CallbackEventModelTest(TestCase):

    def test_default_properties(self):
        pass

    def test_save(self):
        pass

    def test_action_data(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.action_data, ce.event_payload['action']['data'])

    def test_member(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.member, ce.event_payload['action']['memberCreator'])

    def test_board(self):
        ce = CallbackEvent()
        self.assertEqual(ce.board, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.board, ce.event_payload['action']['data']['board'])

    def test_list(self):
        ce = CallbackEvent()
        self.assertEqual(ce.list, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.list, ce.event_payload['action']['data']['list'])

    def test_card(self):
        ce = CallbackEvent()
        self.assertEqual(ce.card, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.card, ce.event_payload['action']['data']['card'])

    def test_member_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.member_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.member_name, ce.event_payload['action']['memberCreator']['fullName'])  # noqa

    def test_board_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.board_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.board_name, ce.event_payload['action']['data']['board']['name'])  # noqa

    def test_list_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.list_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.list_name, ce.event_payload['action']['data']['list']['name'])  # noqa

    def test_card_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.card_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.card_name, ce.event_payload['action']['data']['card']['name'])  # noqa
