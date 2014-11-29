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


class MockTrelloClient(object):
    """Mock the TrelloClient object to return deterministic output.

    The two methods that are used in the app are `create_hook` and
    `list_hooks`. In order to force a deterministic output from these
    we use a class attr, `hooks`, which is a list that is returned
    from the `list_hooks` method.

    In order to force the output simply set the hooks attribute to
    whatever you want to test against, and the `list_hooks` method will
    return it.

    """

    def __init__(self, *args, **kwargs):
        pass

    hooks = []

    def list_hooks(self, token=None):
        """Mock out the list_hooks method to return known hooks."""
        return MockTrelloClient.hooks

    def create_hook(self, callback_url, id_model, desc=None, token=None):
        """Mock out the create_hook method to return fixed WebHook instance."""
        # sentinel value - if id_model = "X" then return False to replicate a
        # failed response from Trello
        if id_model is False:
            return False
        return trello.WebHook(
            self,
            token,
            id_model[::-1],
            desc,
            id_model,
            callback_url,
            True
        )

    @classmethod
    def add_hook(
        cls, client=None, token=None, hook_id=None,
        desc=None, id_model=None, callback_url=None, active=True):
        # adds a WebHook with known properties to the internal collection
        h = trello.WebHook(
            client or MockTrelloClient(),
            token=token,
            hook_id=hook_id,
            desc=desc,
            id_model=id_model,
            callback_url=callback_url,
            active=active
        )
        cls.hooks.append(h)
        return h


class WebhookModelTests(TestCase):

    def setUp(self):
        # clear out the hooks collection on each test
        MockTrelloClient.hooks = []

    def test_str_repr(self):
        hook = Webhook(trello_id='A', trello_model_id='B', auth_token='C')
        self.assertEqual(
            str(hook),
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
            repr(hook),
            u"<Webhook id=%s, trello_id='%s', model='%s'>" %
            (hook.id, hook.trello_id, hook.trello_model_id)
        )

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

    def test_delete(self):
        self.assertEqual(Webhook.objects.count(), 0)
        hook = Webhook().save(sync=False)
        self.assertEqual(Webhook.objects.count(), 1)
        hook.delete()
        self.assertEqual(Webhook.objects.count(), 0)

    def test__client(self):
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

    @mock.patch('trello.TrelloClient', MockTrelloClient)
    def test__fetch(self):
        # no remote hooks, no match
        w = Webhook(auth_token="TOKEN")
        self.assertIsNone(w._fetch())
        # add a hook, but still no match as no model_id
        h = trello.TrelloClient.add_hook(id_model="TEST1")
        self.assertIsNone(w._fetch())
        # update w to match the model id
        w.trello_model_id = h.id_model
        self.assertIsNotNone(w._fetch())
        self.assertEqual(w._fetch(), h)

    @mock.patch('trello.TrelloClient', MockTrelloClient)
    def test__pull(self):
        # if there is no match, then clear out the local trello_id
        w = Webhook(auth_token="TOKEN", trello_model_id="TEST1", trello_id="TEST3")
        self.assertEqual(w.trello_id, "TEST3")
        self.assertIsNone(w._fetch())
        w._pull()
        self.assertEqual(w.trello_id, "")

        # set up a fake remote hook with a matching id
        h = trello.TrelloClient.add_hook(id_model="TEST1", hook_id="TEST2", desc="TEST3")
        # now we do have a matching remote
        self.assertIsNotNone(w._fetch())
        # so we should update the id and description when we pull
        self.assertNotEqual(w.trello_id, h.id)
        self.assertEqual(w.description, "")
        self.assertNotEqual(w.description, h.desc)
        w._pull()
        self.assertEqual(w.trello_id, h.id)
        self.assertEqual(w.description, h.desc)

        # however, if we have an existing description, we should _not_ overwrite
        w.description = "TEST4"
        self.assertNotEqual(w.description, h.desc)
        w._pull()
        self.assertNotEqual(w.description, "TEST4")
        self.assertEqual(w.description, h.desc)

        # confirm that the local object hasn't been saved
        self.assertIsNone(w.id)

    @mock.patch('trello.TrelloClient', MockTrelloClient)
    def test__push(self):
        # test with the False sentinel value, which means that the trello_id
        # should be removed
        w = Webhook(auth_token="TOKEN", trello_id="TEST1", trello_model_id=False)
        self.assertTrue(w.has_trello_id)
        w._push()
        self.assertFalse(w.has_trello_id)

        # now pass in a valid id and check that the trello_id is set
        w = Webhook(auth_token="TOKEN", trello_id="TEST1", trello_model_id="OK")
        self.assertTrue(w.has_trello_id)
        w._push()
        self.assertEqual(w.trello_id, "KO")
        self.assertTrue(w.has_trello_id)

    @mock.patch('trello.TrelloClient', MockTrelloClient)
    def test_sync_true(self):
        self.fail('Write me')

    @mock.patch('trello.TrelloClient', MockTrelloClient)
    def test_sync_false(self):
        # if there is no trello_id, then a sync should update it
        w = Webhook(auth_token="TOKEN", trello_model_id="OK")
        w.sync(save=False)
        self.assertEqual(w.trello_id, "KO")

        # add a remote that looks like the existing w
        h = trello.TrelloClient.add_hook(id_model="OK", hook_id="TEST2", desc="TEST3")
        w.sync(save=False)
        self.assertEqual(w.trello_id, h.id_model)

    def test__touch(self):
        hook = Webhook().save(sync=False)
        self.assertTrue(hook.created_at == hook.last_updated_at)
        hook._touch()
        self.assertTrue(hook.last_updated_at > hook.created_at)

    def test_add_callback(self):
        hook = Webhook().save(sync=False)
        payload = get_sample_data('commentCard', 'json')
        event = hook.add_callback(json.dumps(payload))
        self.assertEqual(event.webhook, hook)
        self.assertEqual(event.event_payload, payload)
        # other CallbackEvent properties are tested in CallbackEvent tests

    def test_callback_url(self):
        hook = Webhook(
            trello_model_id="M",
            auth_token="A",
        ).save(sync=False)
        self.assertEqual(
            hook.callback_url,
            CALLBACK_DOMAIN + hook.get_absolute_url()
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

    def test_member_(self):
        ce = CallbackEvent()
        self.assertEqual(ce.member_, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.member_, ce.event_payload['action']['memberCreator']['fullName'])  # noqa

    def test_board_(self):
        ce = CallbackEvent()
        self.assertEqual(ce.board_, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.board_, ce.event_payload['action']['data']['board']['name'])  # noqa

    def test_list_(self):
        ce = CallbackEvent()
        self.assertEqual(ce.list_, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.list_, ce.event_payload['action']['data']['list']['name'])  # noqa

    def test_card_(self):
        ce = CallbackEvent()
        self.assertEqual(ce.card_, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.card_, ce.event_payload['action']['data']['card']['name'])  # noqa
