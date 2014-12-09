# # -*- coding: utf-8 -*-
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(needs_autoescape=True)
def render_media(attachment, autoescape=None):
    """Future-named filter, but we only support images for the time being."""
    format_str = '%s'
    # handle input escaping explicitly so we can mark our HTML output as safe
    url = conditional_escape(attachment.get('url')) if autoescape else attachment.get('url')
    if attachment.get('type') == 'image':
        format_str = '<img src="%s">'
    return mark_safe(format_str % url)