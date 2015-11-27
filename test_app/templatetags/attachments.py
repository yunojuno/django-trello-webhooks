from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_attachment(attachment):
    """Returns the attachment in an img tag where necessary
    """
    if attachment.get('image') is True:
        return mark_safe("<img src='{}'>".format(attachment.get('url')))
    else:
        return attachment['name']
