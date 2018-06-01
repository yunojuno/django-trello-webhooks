from django.test import TestCase

from test_app.templatetags.test_app_tags import is_image


class TemplateTagsTests(TestCase):

    def test_is_image_with_image_mime(self):
        mime = 'image/jpg'
        self.assertTrue(is_image(mime))

    def test_is_image_with_non_image_mime(self):
        mime = 'text/plain'
        self.assertFalse(is_image(mime))

    def test_is_image_with_None(self):
        self.assertFalse(is_image(None))
