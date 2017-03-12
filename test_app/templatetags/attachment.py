from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def format_attachment(attachment):
    if attachment.get('content_type', '').startswith('image'):
        return mark_safe("<img src='%s'>" % attachment.get('url'))
    else:
        return attachment.get('name')
