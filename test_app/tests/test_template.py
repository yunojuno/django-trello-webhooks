# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.test import TestCase


class TemplateTests(TestCase):

    def test_addAttachmentToCard(self):
        template = 'trello_webhooks/addAttachmentToCard.html'

        # attachement is an image
        url = 'http://example.com/img.png'
        context = {"action": {"data": {"attachment":{"url": url}}}}
        result = render_to_string(template, context)
        self.assertIn('<img src="http://example.com/img.png">', result)

        # attachement is *not* an image
        url = 'http://example.com/main.js'
        context = {"action": {"data": {"attachment":{"url": url,"name": "main.js"}}}}
        result = render_to_string(template, context)
        self.assertIn('"<strong>main.js</strong>"', result)
