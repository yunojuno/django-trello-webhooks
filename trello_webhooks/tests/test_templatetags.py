# -*- coding: utf-8 -*-
from django.test import TestCase

from trello_webhooks.settings import TRELLO_API_KEY
from trello_webhooks.templatetags.trello_webhook_tags import (
    trello_api_key,
    trello_updates
)


class TemplateTagTests(TestCase):

    def test_trello_api_key(self):
        self.assertEqual(trello_api_key(), TRELLO_API_KEY)

    def test_trello_updates(self):
        # good data:
        old = {'pos': 1}
        new = {'pos': 2, 'abc': 'xyz'}
        self.assertEqual(
            trello_updates(new, old),
            {'pos': (1, 2)}
        )

        # bad data
        new = {}
        self.assertEqual(
            trello_updates(new, old),
            {'pos': (1, None)}
        )
