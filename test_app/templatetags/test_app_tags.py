from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def display_attachment(attachment):
    """If the attachment is an image return an img tag, otherwise return the 
    attachment filename.
    """
    if attachment.get('contentType', '').startswith('image'):
        # Use the cropped image if it exists.
        url = attachment.get('previewUrl', attachment['url'])
        return mark_safe("<img src='%s'>" % url)
    else:
        return attachment["name"]
