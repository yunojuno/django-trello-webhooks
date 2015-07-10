from django.test import TestCase

from test_app.templatetags.test_app_tags import display_attachment


class TemplateTagTests(TestCase):

    def test_display_attachment(self):
        attachment = {
            'name': 'test-image.jpg',
            'url': 'https://example.com/test-image.jpg',
        }
        # No content type means the filename should be displayed.
        self.assertEqual(display_attachment(attachment), attachment['name'])
        # Non image content type should return filename.
        attachment['contentType'] = 'text/plain'
        self.assertEqual(display_attachment(attachment), attachment['name'])
        # Image content type should return a img tag.
        attachment['contentType'] = 'image/jpeg'
        self.assertEqual(display_attachment(attachment), "<img src='%s'>" % attachment['url'])
        # Preview image should be used if available.
        attachment['previewUrl'] = 'https://example.com/cropped/test-image.jpg'
        self.assertEqual(display_attachment(attachment), "<img src='%s'>" % attachment['previewUrl'])
