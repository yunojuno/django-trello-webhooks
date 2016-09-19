# -*- coding: utf-8 -*-
import json
from django.test import TestCase

from trello_webhooks.tests import get_sample_data
from trello_webhooks.models import CallbackEvent


def change_extension(data, new_extension):
    data_json = json.loads(data)
    new_url = data_json['action']['data']['attachment']['url'][:-3] + new_extension
    data_json['action']['data']['attachment']['url'] = new_url
    data = json.dumps(data_json)
    return data


class CallbackEventModelTest(TestCase):

    def test_default_properties(self):
        pass

    def test_save(self):
        pass

    def test_action_data(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.action_data, ce.event_payload['action']['data'])

    def test_add_attachment_to_card(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        ce.event_payload = get_sample_data('addAttachmentToCard', 'text')
        self.assertIn('attachment', ce.action_data)
        self.assertEqual(ce.action_data, ce.event_payload['action']['data'])

    def test_resolve_content_type_jpeg(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        ce.event_payload = get_sample_data('addAttachmentToCard', 'text')
        self.assertIn('attachment', ce.action_data)
        the_file = ce.action_data['attachment']['url']
        content_type = ce.resolve_content_type(the_file)

        self.assertEqual(content_type, 'image/jpeg')
        self.assertEqual(ce.action_data['attachment']['content_type'], 'image/jpeg')

    def test_resolve_content_type_png(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        data = get_sample_data('addAttachmentToCard', 'text')

        #--------------------------------
        # Change ext to PNG
        #⨪-------------------------------
        data = change_extension(data, 'png')
        ce.event_payload = data
        self.assertIn('attachment', ce.action_data)
        the_file = ce.action_data['attachment']['url']
        content_type = ce.resolve_content_type(the_file)

        self.assertEqual(content_type, 'image/png')
        self.assertEqual(ce.action_data['attachment']['content_type'], 'image/png')

    def test_resolve_content_type_python(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        data = get_sample_data('addAttachmentToCard', 'text')

        #--------------------------------
        # Change ext to Python
        #⨪-------------------------------
        data = change_extension(data, 'py')
        ce.event_payload = data
        self.assertIn('attachment', ce.action_data)
        the_file = ce.action_data['attachment']['url']
        content_type = ce.resolve_content_type(the_file)

        self.assertEqual(content_type, 'text/x-python')
        self.assertEqual(ce.action_data['attachment']['content_type'], 'text/x-python')

    def test_resolve_content_type_unrecognised(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        data = get_sample_data('addAttachmentToCard', 'text')
        #--------------------------------
        # Change ext to impossible ext
        #⨪-------------------------------
        data = change_extension(data, 'NO-IDEA-OF-WHAT-THIS-IS')
        ce.event_payload = data
        self.assertIn('attachment', ce.action_data)
        the_file = ce.action_data['attachment']['url']
        content_type = ce.resolve_content_type(the_file)

        self.assertIsNone(content_type)
        self.assertIsNone(ce.action_data['attachment']['content_type'])

    def test_member(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.member, ce.event_payload['action']['memberCreator'])

    def test_board(self):
        ce = CallbackEvent()
        self.assertEqual(ce.board, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.board, ce.event_payload['action']['data']['board'])

    def test_list(self):
        ce = CallbackEvent()
        self.assertEqual(ce.list, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.list, ce.event_payload['action']['data']['list'])

    def test_card(self):
        ce = CallbackEvent()
        self.assertEqual(ce.card, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.card, ce.event_payload['action']['data']['card'])

    def test_member_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.member_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.member_name, ce.event_payload['action']['memberCreator']['fullName'])  # noqa

    def test_board_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.board_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.board_name, ce.event_payload['action']['data']['board']['name'])  # noqa

    def test_list_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.list_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.list_name, ce.event_payload['action']['data']['list']['name'])  # noqa

    def test_card_name(self):
        ce = CallbackEvent()
        self.assertEqual(ce.card_name, None)
        ce.event_payload = get_sample_data('createCard', 'text')
        self.assertEqual(ce.card_name, ce.event_payload['action']['data']['card']['name'])  # noqa
