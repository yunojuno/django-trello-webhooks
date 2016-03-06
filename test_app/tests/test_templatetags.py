# -*- coding: utf-8 -*-
from django.test import TestCase

from test_app.templatetags.test_app_tags import render_attachment


class TemplateTagTests(TestCase):
    def test_render_attachment(self):
        # Test empty mime type
        attachment = {
            'url': 'http://example.com/foo.ext',
            'name': 'foo.ext',
            'mimeType': None,
        }
        self.assertEqual(
            render_attachment(attachment),
            '"foo.ext"'
        )

        # Test random mime type
        attachment['mimeType'] = 'html/text'
        self.assertEqual(
            render_attachment(attachment),
            '"foo.ext"'
        )

        # Test image mime type
        attachment['mimeType'] = 'image/png'
        self.assertEqual(
            render_attachment(attachment),
            '<br><img src="http://example.com/foo.ext" alt="foo.ext">'
        )
