# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.template import Context, Template
from django.test import TestCase

from trello_webhooks.models import CallbackEvent


class TemplateTagTests(TestCase):

    @staticmethod
    def create_event_with_attachment(url):
        return CallbackEvent(
            event_payload={
                'action': {
                    'data': {
                        'attachment': {
                            'url': url,
                            'name': 'jim',
                        }
                    }
                }
            }
        )

    @staticmethod
    def create_soup_from_event(event):
        template = Template("""
            {% load render_attachment from attachment_tags %}
            {% render_attachment attachment %}
        """)
        context = Context(event.action_data)
        return BeautifulSoup(template.render(context), 'html.parser')

    def test_renders_image(self):
        """
        given a url that looks like an image is attached
        when the template tag renders
        then an <img> is rendered
        and the src attribute is set

        """
        url = 'http://i.imgur.com/RLsdIVe.jpg'
        event = self.create_event_with_attachment(url)
        soup = self.create_soup_from_event(event)
        self.assertEqual(soup.find('a')['href'], url)
        self.assertEqual(soup.find('img')['src'], url)

    def test_renders_other(self):
        """
        given a url that does not look like an image is attached
        when the template tag renders
        then an <img> is not rendered
        but an <a> tag is rendered
        and the href attribute is set

        """
        url = 'http://i.imgur.com/RLsdIVe'
        event = self.create_event_with_attachment(url)
        soup = self.create_soup_from_event(event)
        self.assertEqual(soup.find('img'), None)
        self.assertEqual(soup.find('a')['href'], url)
