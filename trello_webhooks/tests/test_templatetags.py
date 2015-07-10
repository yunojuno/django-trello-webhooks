# -*- coding: utf-8 -*-
from django.test import TestCase
from nose.tools import assert_equal

from trello_webhooks.tests import get_sample_data
from trello_webhooks import contenttypes
from trello_webhooks.settings import TRELLO_API_KEY
from trello_webhooks.templatetags.trello_webhook_tags import (
    trello_api_key,
    trello_updates,
    get_attachment_link,
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


def test_attachment_rendering():
    test_data = [
        ({'contentType': 'image/png', u'url': u'foo.com', 'name': u'FOO'}, u'<a href="foo.com"><img src="foo.com"></a>'),
        ({'contentType': 'application/json', u'url': u'bar.com', 'name': u'BAR'}, u'<a href="bar.com">BAR</a>'),
        ({u'url': u'baz.com', 'name': u'BAZ'}, u'<a href="baz.com">BAZ</a>'),
    ]
    for att, expected in test_data:
        yield check_get_attachment_link, att, expected


def check_get_attachment_link(attachment, expected):
    link = get_attachment_link(attachment)
    assert_equal(link, expected)
