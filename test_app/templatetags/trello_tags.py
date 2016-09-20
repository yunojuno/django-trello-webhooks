from django import template
from django.template import Context
from django.template.loader import get_template


register = template.Library()


@register.simple_tag()
def trello_media(attachment):
    """Renders an <img> or plain text depending on the attachment mime type."""
    template = get_template('template_tags/media_tag.html')

    content_type = attachment.get('content_type', "NO-CONTENT-TYPE")

    is_image = False
    if content_type and content_type.startswith('image/'):
        is_image = True

    ctx = Context({'attachment': attachment, "is_image": is_image})

    return template.render(ctx)
