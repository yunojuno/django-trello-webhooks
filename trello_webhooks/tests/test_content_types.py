# -*- coding: utf-8 -*-
from django.test import TestCase

from mock import patch
import requests
import httpretty

from trello_webhooks import content_types


def raise_exception(request, uri, headers):
    raise requests.RequestException('Something went horribly wrong')


class ContentTypeTests(TestCase):
    def test_is_image(self):
        self.assertTrue(content_types.is_image("image/png"))
        self.assertTrue(content_types.is_image("image/jpeg"))
        self.assertTrue(content_types.is_image("image/gif"))
        self.assertFalse(content_types.is_image("video/mp4"))
        self.assertFalse(content_types.is_image("something random"))

    @patch.object(content_types, 'request_content_type',
                  return_value="image/png")
    def test_guess_url_content_type(self, mock_request_content_type):
        sample_url = "http://example.com/some_image.jpg"
        sample_url_no_ext = "http://example.com/i_have_no_extension"

        ct = content_types.guess_url_content_type(sample_url)
        self.assertEqual(ct, "image/jpeg")
        self.assertFalse(mock_request_content_type.called)

        ct = content_types.guess_url_content_type(sample_url_no_ext)
        self.assertEqual(ct, "image/png")
        mock_request_content_type.assert_called_once_with(sample_url_no_ext)

    @httpretty.activate
    def test_request_content_type(self):
        sample_url = "http://example.com/anything"
        httpretty.register_uri(
            httpretty.HEAD, sample_url, status=200,
            content_type='image/gif'
        )
        ct = content_types.request_content_type(sample_url)
        self.assertEqual(ct, 'image/gif')

        httpretty.register_uri(
            httpretty.HEAD, sample_url,
            body=raise_exception
        )
        try:
            content_types.request_content_type(sample_url)
        except requests.RequestException:
            self.fail("requests exception not handled")
