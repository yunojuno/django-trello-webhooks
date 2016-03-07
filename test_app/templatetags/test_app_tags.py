from django.utils.html import format_html
from trello_webhooks import content_types
from trello_webhooks.templatetags.trello_webhook_tags import register


@register.filter
def render_attachment(attachment):
    """Render a card attachment

    This will return either the name of the file or an img tag
    if the attachment content type is an image.

    Args:
        attachment: an event data attachment dictionary
    Returns:
        an html string representation of the attachment
    """
    if content_types.is_image(attachment.get('mimeType') or ''):
        return format_html(
            '<br><img src="{}" alt="{}">',
            attachment.get('url') or '',
            attachment.get('name') or '',
        )
    return '"{}"'.format(attachment.get('name'))