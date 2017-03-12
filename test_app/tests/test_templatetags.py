from django.test import TestCase

from test_app.templatetags.attachment import format_attachment

class AttachmentTemplateTagTests(TestCase):

    def test_display_inline_images(self):
        attachment = {
            'name': 'test-image.jpg',
            'url': 'https://example.com/test-image.jpg',
            'content_type': 'image/jpeg'
        }
        self.assertEqual(format_attachment(attachment), "<img src='%s'>" % attachment['url'])

    def test_display_name_for_attachments_other_than_images(self):
        attachment = {
            'name': 'test-csv.csv',
            'url': 'https://test-csv.csv',
            'content_type': 'text/csv'
        }
        self.assertEqual(format_attachment(attachment), "test-csv.csv")