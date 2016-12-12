# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def render_attachment(attachment):
    """Returns attachment image inline if one is present, returns attachment name if not"""
    if attachment.get('mainType') == 'image':
        return mark_safe('<img src="{0}">'.format(attachment.get('url')))

    return '"' + attachment.get('name') + '"'