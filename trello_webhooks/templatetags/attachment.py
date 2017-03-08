# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def is_image(attachment):
    return attachment.get('previewUrl', False)


@register.filter()
def render_attachment(attachment):
    """Returns attachment image inline if one is present, returns attachment name if not"""
    if is_image(attachment):
        return mark_safe('<img src="%s">' % attachment.get('url'))
    return '"%s"' % attachment.get('name')