# -*- coding: utf-8 -*-
import datetime
import json
# import mock
# from os import path

from django.core.urlresolvers import reverse
from django.test import TestCase

# import trello

# from trello_webhooks.settings import (
#     TRELLO_API_KEY,
#     TRELLO_API_SECRET,
#     CALLBACK_DOMAIN
# )
from trello_webhooks.models import Webhook, CallbackEvent


class WebhookViewTests(TestCase):
    pass

    def setUp(self):
        self.url = reverse(
            'trello_callback_url',
            kwargs={'auth_token': 'A', 'trello_model_id': '123'}
        )

    def test_head(self):
        print "----------------"
        print self.url
        resp = self.client.head(self.url)
        # self.assertContains
        print resp
        print "----------------"
