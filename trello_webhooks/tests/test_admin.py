# -*- coding: utf-8 -*-
from django.test import TestCase
from django.template.defaultfilters import truncatewords, truncatechars

from trello_webhooks.admin import CallbackEventAdmin, WebhookAdmin
from trello_webhooks.models import Webhook, CallbackEvent


class CallbackEventAdminTests(TestCase):

    def setUp(self):
        self.webhook = Webhook(auth_token="ABC").save(sync=False)
        self.event = CallbackEvent(
            webhook=self.webhook,
            event_type='commentCard'
        ).save()
        self.admin = CallbackEventAdmin(CallbackEvent, None)
        self.webhook_admin = WebhookAdmin(Webhook, None)

    def test_webhook_(self):
        self.assertEqual(
            self.admin.webhook_(self.event),
            self.webhook.id
        )

    def test_has_template(self):
        self.assertTrue(self.admin.has_template(self.event))
        self.event.event_type = "X"
        self.assertFalse(self.admin.has_template(self.event))

    def test_rendered(self):
        self.assertIsNotNone(self.admin.rendered(self.event))
        self.event.event_type = "X"
        self.assertIsNone(self.admin.rendered(self.event))

    def test_board_(self):
        self.event.event_payload = {
            "action": {
                "data": {
                    "board": {
                        "id": "5476fab52086e26047fa328c",
                        "name": "Django Trello Webhooks Test Board",
                        "shortLink": "TAAnwdP9"
                    },
                },
            },
        }
        self.assertEqual(
            self.admin.board_(self.event),
            truncatewords(self.event.board_name, 3))

    def test_list_(self):
        self.event.event_payload = {
            "action": {
                "data": {
                    "list": {
                        "name": "To Do",
                        "id": "5476fb3271e6d2370b31e986"
                    }
                },
            },
        }
        self.assertEqual(
            self.admin.list_(self.event),
            truncatewords(self.event.list_name, 3))

    def test_card_(self):
        self.event.event_payload = {
            "action": {
                "data": {
                    "card": {
                        "shortLink": "4K7LwAKx",
                        "idShort": 1,
                        "name": "Test card",
                        "id": "5476fb7437746ac807afe2a5"
                    }
                },
            },
        }
        self.assertEqual(
            self.admin.card_(self.event),
            truncatewords(self.event.card_name, 3))

    def test_auth_token_(self):
        self.assertEqual(
            self.webhook_admin.auth_token_(self.webhook),
            self.webhook.auth_token)
