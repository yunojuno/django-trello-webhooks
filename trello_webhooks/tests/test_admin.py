# -*- coding: utf-8 -*-
from django.test import TestCase

from trello_webhooks.admin import CallbackEventAdmin
from trello_webhooks.models import Webhook, CallbackEvent


class CallbackEventAdminTests(TestCase):

    def setUp(self):
        self.webhook = Webhook(auth_token="ABC").save(sync=False)
        self.event = CallbackEvent(
            webhook=self.webhook,
            event_type='commentCard'
        ).save()
        self.admin = CallbackEventAdmin(CallbackEvent, None)

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
