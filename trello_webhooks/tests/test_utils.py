# -*- coding: utf-8 -*-
from django.test import TestCase
from trello_webhooks.utils import (
    get_mimetype, get_attachment_type, render_template_for_attachment
)


class MimeTypeCheckTests(TestCase):
    def test_correct_mimetype(self):
        mime_type = get_mimetype('testimage.jpg')
        self.assertEqual(mime_type, ('image/jpeg', None))

    def test_unknown_mimetype(self):
        mime_type = get_mimetype('testimage')
        self.assertEqual(mime_type, ('None/None', 'None'))

    def test_attachment_type(self):
        attachment_type = get_attachment_type(('image/jpeg', None))
        self.assertEqual(attachment_type, 'image')

    def test_render_template_for_attachment(self):
        rendered = render_template_for_attachment(
            {'name': 'test', 'url': 'test.jpeg'}
        )
        self.assertEqual(
            u'<img src="test.jpeg" alt="test" width="200" height="200"/>',
            rendered
        )
