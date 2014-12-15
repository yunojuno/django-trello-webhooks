import re

from django import template
from django.utils.safestring import mark_safe


register = template.Library()

IMAGE_RE = re.compile(r'image/.*', re.I)


@register.filter
def as_inline_image(attachment):
	"""
	Renders attachment as an <a> tag, with an inline <img> tag
	   when it's an image.
	If it's not an image, just shows an <a> tag with its name.

	Example:
	- When the attachment is an image
		"attachment": {
            "mimeType": "image/png",
            "name": "example.png",
            "url": "http://www.example.org/example.png"
        }
        {{attachment|as_inline_image}} => <a href='http://www.example.org/example.png'><img src='http://www.example.org/example.png'></a>

    - When the attachment is not an image
		"attachment": {
            "mimeType": "text/html",
            "name": "example.html",
            "url": "http://www.example.org/example.html"
        }
        {{attachment|as_inline_image}} => <a href='http://www.example.org/example.html'>example.html</a>

	"""
	mimetype = attachment.get('mimeType')
	if mimetype and re.match(IMAGE_RE, mimetype):
		res = "<a href='{url}'><img src='{url}'></a>".format(
			url=attachment.get('url')
		)
	else:
		res = "<a href='{url}'>{name}</a>".format(
			url=attachment.get('url'),
			name=attachment.get('name')
		)
	return mark_safe(res)
