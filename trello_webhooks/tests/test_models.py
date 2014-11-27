# -*- coding: utf-8 -*-
import datetime
import json
from os import path

from django.test import TestCase

from trello_webhooks.settings import TRELLO_API_KEY, TRELLO_API_SECRET
from trello_webhooks.models import Webhook


class WebhookModelTests(TestCase):

    def setUp(self):
        self.payload_path = path.join(
            path.abspath(path.dirname(__file__)),
            'sample_data/createCard.json'
        )

    def _test_payload(self, format_):
        """Return test JSON payload as 'json' or 'text' object.

        Args:
            format_: string, one of either 'json' or 'text'
        """
        _path = path.join(
            path.abspath(path.dirname(__file__)),
            'sample_data/createCard.json'
        )
        with open(_path, 'r') as f:
            return f.read() if format_ == 'text' else json.load(f)

    def test_default_properties(self):
        hook = Webhook()
        self.assertEqual(hook.id, None)
        self.assertEqual(hook.trello_model_id, '')
        self.assertEqual(hook.trello_id, '')
        self.assertEqual(hook.description, '')
        self.assertEqual(hook.created_at, None)
        self.assertEqual(hook.auth_token, '')

    def test_save_no_sync(self):
        # Check that save updates the timestamps
        hook = Webhook().save(sync=False)
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

    def test_delete(self):
        self.fail('Write me')

    def test__client(self):
        # should fail without a token
        w = Webhook()
        self.assertRaises(AssertionError, w._client)
        w.auth_token = 'X'
        client = w._client()
        self.assertEqual(client.api_key, TRELLO_API_KEY)
        self.assertEqual(client.api_secret, TRELLO_API_SECRET)
        self.assertEqual(client.resource_owner_key, w.auth_token)
        self.assertEqual(client.resource_owner_secret, None)

    def test__fetch(self):
        self.fail('Write me')

    def test__pull(self):
        self.fail('Write me')

    def test__push(self):
        self.fail('Write me')

    def test__touch(self):
        hook = Webhook().save(sync=False)
        self.assertTrue(hook.created_at == hook.last_updated_at)
        hook._touch()
        self.assertTrue(hook.last_updated_at > hook.created_at)

    def test_add_callback(self):
        hook = Webhook().save(sync=False)
        payload = self._test_payload('json')
        event = hook.add_callback(json.dumps(payload))
        self.assertEqual(event.webhook, hook)
        self.assertEqual(event.event_payload, payload)
        # other CallbackEvent properties are tested in CallbackEvent tests

    def test_callback_url(self):
        self.fail('Write me')

    def test_get_absolute_url(self):
        self.fail('Write me')

    def test_has_trello_id(self):
        self.fail('Write me')

    def test_sync(self):
        self.fail('Write me')
