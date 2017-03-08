# -*- coding: utf-8 -*-
from django.test import TestCase

from trello_webhooks.settings import TRELLO_API_KEY
from trello_webhooks.templatetags.attachments import render_attachment
from trello_webhooks.templatetags.trello_webhook_tags import (
    trello_api_key,
    trello_updates
)


class TemplateTagTests(TestCase):
    def setUp(self):
        self.plain_attachment = {
            "name": "name.png",
            "url": "https://test.com/name.png"
        }

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

    def test_attachments_no_type(self):
        # No contentType => name is displayed.
        self.assertEqual(
            render_attachment(self.plain_attachment),
            self.plain_attachment['name']
        )

    def test_attachments_video_type(self):
        # contentType != image => name is displayed.
        self.plain_attachment['contentType'] = 'video/mp4'

        self.assertEqual(
            render_attachment(self.plain_attachment),
            self.plain_attachment['name']
        )

    def test_attachments_image_type(self):
        # contentType==image => image is displayed.
        self.plain_attachment['contentType'] = 'image/jpeg'

        self.assertEqual(
            render_attachment(self.plain_attachment),
            '<img src="%s">' % self.plain_attachment['url']
        )

    def test_attachments_previewUrl(self):
        # if previewUrl exists => it's used
        self.plain_attachment.update({
            'contentType': 'image/png',
            'previewUrl': 'https://test.com/200x200/name.png'
        })

        self.assertEqual(
            render_attachment(self.plain_attachment),
            '<img src="%s">' % self.plain_attachment['previewUrl']
        )
