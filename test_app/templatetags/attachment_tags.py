from django import template


register = template.Library()


@register.inclusion_tag('trello_webhooks/partials/attachment.html')
def render_attachment(attachment):
    """
    Template tag that renders an inline image if the attachment looks like an
    image, otherwise it renders an anchor tag.

    Args:
        attachment: dict, the contents of the 'attachment' key from
            CallbackEvent action data

    """
    return {
        'is_image': attachment['content_type'].startswith('image'),
        'url': attachment['url'],
        'name': attachment['name'],
    }
