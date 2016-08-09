from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag
def display_attachment_html(data):
    """
    Render a piece of a HTML in a template

    Receives a dict containing the Trello payload and return a HTML
    with an image if found an image attachment. Otherwise it'll return
    a HTML with a non-image renderization.

    data = {
        "action": {
            "data": {
                "attachment": {
                    "id": "549029d1fb1ce0bfa8f05117",
                    "mimeType": 'image/png',
                },
            }
        }
    }

    From this we can see that will return the image HTML.
    """
    if (data['action']['data']['attachment'] and
            'image' in data['action']['data']['attachment']['mimeType']):
        to_be_rendered = "<strong>{% if action.data.attachment and 'image' in type_attachment %}<a href='{{action.data.attachment.url}}'><img src='{{action.data.attachment.url}}'></a>{% else %}<a href='{{action.data.attachment.url}}'>{{action.data.attachment.name}}</a>{% endif %}</strong>"
        return mark_safe(to_be_rendered)
    else:
        return mark_safe(
            "<strong><a href='{{action.data.attachment.url}}'>{{action.data.attachment.name}}</a></strong>")
