from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter(name='attachment_name_or_image')
def attachment_name_or_image(value):
	if value.attachment_content_type.startswith('image/'):
		return mark_safe("<img src='%s'/>" % value.attachment_url)
	else:
		return value.attachment_name
