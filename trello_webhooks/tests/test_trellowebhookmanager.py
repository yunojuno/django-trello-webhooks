# -*- coding: utf-8 -*-

from django.test import TestCase

from trello_webhooks.models import TrelloWebhookManager


class TrelloClientMock(object):
    def list_hooks(self, token):
        if token == "RIGHT-TOKEN":
            return [1, 2, 3]
        return []


class TrelloWebhookManagerTests(TestCase):
    def setUp(self):
        self.manager = TrelloWebhookManager(client=TrelloClientMock())

    def test_get_hooks_right_token(self):
        tokens = self.manager.list_hooks(auth_token="RIGHT-TOKEN")
        self.assertEqual(tokens, [1, 2, 3])

    def test_get_hooks_wrong_token(self):
        tokens = self.manager.list_hooks(auth_token="WRONG-TOKEN")
        self.assertEqual(tokens, [])
