# -*- coding: utf-8 -*-

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def is_image(attachment):
    return attachment.get('contentType', '').startswith('image')


@register.filter()
def render_attachment(attachment):
    """Return inline image if attachment is an image, otherwise - its name"""
    if is_image(attachment):
        preview_url = attachment.get('previewUrl', attachment['url'])

        return mark_safe('<img src="%s">' % preview_url)
    return attachment['name']
