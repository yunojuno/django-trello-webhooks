# -*- coding: utf-8 -*-
from django.conf import settings

import requests

HIPCHAT_API_URL = 'https://simpleoption.hipchat.com/v2/room/{room_id}/notification?auth_token={auth_token}'


def send_to_hipchat(message,
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
        'notify': notify,
        'color': color,
        'message': message,
        'message_format': 'html',
    }


    url = HIPCHAT_API_URL.format(room_id=room, auth_token=token)

    resp = requests.post(url, json=payload)

    return resp.status_code
