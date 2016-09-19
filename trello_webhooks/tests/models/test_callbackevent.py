# -*- coding: utf-8 -*-
from django.test import TestCase

from trello_webhooks.tests import get_sample_data
from trello_webhooks.models import CallbackEvent



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


    def test_resolve_content_type_jpg(self):
        ce = CallbackEvent()
        self.assertEqual(ce.action_data, None)
        ce.event_payload = get_sample_data('addAttachmentToCard', 'text')
        self.assertIn('attachment', ce.action_data)
        the_file = ce.action_data['attachment']['url']
        content_type = ce.resolve_content_type(the_file)
        self.assertEqual(content_type, 'image/jpg')


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
