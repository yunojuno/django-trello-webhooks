# -*- coding: utf-8 -*-
import datetime
import json
import mock

from django.test import TestCase
from django.core.urlresolvers import reverse

from trello_webhooks.tests import get_sample_data
from trello_webhooks.utils.testing import mock_trello_sync
from trello_webhooks.models import Webhook
from trello_webhooks.settings import (
    TRELLO_API_KEY,
    TRELLO_API_SECRET,
    CALLBACK_DOMAIN
)


class TrelloClientMock(object):
    def fetch_json(self, url, http_method, post_args):
        if http_method == "OK_CALL":
            return {'id': 1111, 'active': True}



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

    def test_trello_sync_ok(self):
        w = Webhook(trello_model_id=999,
                    auth_token="TOKEN").save(sync=False)
        self.assertEqual(w.is_active, None)

        w._trello_sync(verb="OK_CALL", trello_client=TrelloClientMock())

        self.assertEqual(w.is_active, True)
        self.assertEqual(w.trello_id, 1111)
