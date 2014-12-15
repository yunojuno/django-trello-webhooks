# -*- coding: utf-8 -*-
from django.test import TestCase

from test_app.templatetags.attachment_filters import (
    as_inline_image,
)


class TemplateTagTests(TestCase):
    def test_as_inline_image(self):
        attachment = {
            "mimeType": "image/png",
            "name": "example.png",
            "url": "http://www.example.org/example.png"
        }
        expected = ("<a href='http://www.example.org/example.png'>"
                    "<img src='http://www.example.org/example.png'></a>")
        self.assertEqual(as_inline_image(attachment), expected)

        attachment = {
            "mimeType": "text/html",
            "name": "example.html",
            "url": "http://www.example.org/example.html"
        }
        expected = "<a href='http://www.example.org/example.html'>example.html</a>"
        self.assertEqual(as_inline_image(attachment), expected)
