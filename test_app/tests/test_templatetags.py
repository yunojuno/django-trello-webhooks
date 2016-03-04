
from django.test import TestCase

from test_app.templatetags.test_app_tags import is_image


class TemplateTagsTests(TestCase):

    def test_is_image(self):
        # no attachment
        value = ''
        result = is_image(value)
        self.assertFalse(result)

        # attachment is an image
        value = 'http://example.com/img.png'
        result = is_image(value)
        self.assertTrue(result)

        # attachment is *not* an image
        value = 'http://example.com/main.js'
        result = is_image(value)
        self.assertFalse(result)
