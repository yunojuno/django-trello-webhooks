# -*- coding: utf-8 -*-
from django.conf import settings

import requests

HIPCHAT_API_URL = 'https://api.hipchat.com/v2/room/%s/notification'


def send_to_hipchat(
    message,
    token=settings.HIPCHAT_API_TOKEN,
    room=settings.HIPCHAT_ROOM_ID,
    sender="Trello",
    color="yellow",
    notify=False):
    """
    Send a message to HipChat.

    Returns the status code of the request. Should be 200.
    """
    payload = {
        'auth_token': token,
        'notify': notify,
        'color': color,
        'from': sender,
        'room_id': room,
        'message': message
    }
    return requests.post(HIPCHAT_API_URL % room, data=payload).status_code
