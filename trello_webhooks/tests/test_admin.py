# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from trello_webhooks.admin import CallbackEventAdmin
from trello_webhooks.models import Webhook, CallbackEvent
from trello_webhooks.tests import get_sample_data


class MockResponse():
    def iter_content(self, chunk_size):
        return [1, 2]

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self):
        return self


class CallbackEventAdminTests(TestCase):

    def setUp(self):
        self.webhook = Webhook(auth_token="ABC").save(sync=False)
        self.event = CallbackEvent(
            webhook=self.webhook,
            event_type='commentCard'
        ).save()
        self.admin = CallbackEventAdmin(CallbackEvent, None)

    def test_webhook_(self):
        self.assertEqual(
            self.admin.webhook_(self.event),
            self.webhook.id
        )

    def test_has_template(self):
        self.assertTrue(self.admin.has_template(self.event))
        self.event.event_type = "X"
        self.assertFalse(self.admin.has_template(self.event))

    def test_rendered(self):
        self.assertIsNotNone(self.admin.rendered(self.event))
        self.event.event_type = "X"
        self.assertIsNone(self.admin.rendered(self.event))

    @mock.patch('trello_webhooks.models.requests.get', return_value=MockResponse())
    @mock.patch('trello_webhooks.models.magic.from_buffer', return_value='image/png')
    @mock.patch('trello_webhooks.admin.logger')
    def test_add_attachment_type(self, mock_logger, mock_from_buffer, mock_response):
        mock_request = mock.Mock()
        mock_request.user = 'test_user'
        # Create a CallbackEvent object with attachment but no attachment type.
        hook = Webhook().save(sync=False)
        payload = get_sample_data('addAttachmentToCardImageType', 'json')
        event = CallbackEvent(
            webhook=hook,
            event_type='addAttachmentToCard',
            event_payload=payload
        )
        event.save()
        queryset = CallbackEvent.objects.all()
        # Run helper function to add the missing attachment type.
        self.admin.add_attachment_type(mock_request, queryset)
        # Reload event objects from the database after it was updated.
        # Since we create one CallbackEvent object in setUp the id of the one we
        # need to confirm was changed will be id=2
        event = CallbackEvent.objects.get(id=2)
        self.assertEqual(
            event.event_payload['action']['data']['attachment']['attachmentType'], 'image/png')
        mock_logger.info.assert_called_once_with(
            '%s added attachment type to %i CallbackEvents from the admin site.', 'test_user', 1)
