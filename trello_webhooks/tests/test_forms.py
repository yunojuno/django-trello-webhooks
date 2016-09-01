# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from django.test import TestCase

from trello_webhooks.forms import WebhookForm


class WebhookFormTest(TestCase):

    def test_renders_auth_token_button(self):
        form = WebhookForm()
        soup =  BeautifulSoup(form.as_table(), 'html.parser')
        self.assertEqual(soup.find('a')['onclick'], 'getTrelloToken()')
