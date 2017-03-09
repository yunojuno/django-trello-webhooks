# -*- coding: utf-8 -*-
from django.test import TestCase

from test_app.templatetags.test_app_tags import render_attachment


class TemplateTagTests(TestCase):
    def setUp(self):
        self.attachment_without_type = {
            "name": "name.png",
            "url": "https://test.com/name.png"
        }

    def test_attachments_no_type(self):
        self.assertEqual(
            render_attachment(self.attachment_without_type),
            self.attachment_without_type['name']
        )

    def test_attachments_video_type(self):
        self.attachment_without_type.update({'contentType': 'video/mp4'})
        video_attachment = self.attachment_without_type

        self.assertEqual(
            render_attachment(video_attachment),
            video_attachment['name']
        )

    def test_attachments_image_type(self):
        self.attachment_without_type.update({'contentType': 'image/jpeg'})
        image_attachment = self.attachment_without_type

        self.assertEqual(
            render_attachment(image_attachment),
            '<img src="%s">' % image_attachment ['url']
        )

    def test_attachments_previewUrl(self):
        self.attachment_without_type.update({
            'contentType': 'image/png',
            'previewUrl': 'https://test.com/200x200/name.png'
        })
        image_attachment = self.attachment_without_type

        self.assertEqual(
            render_attachment(image_attachment),
            '<img src="%s">' % image_attachment['previewUrl']
        )
