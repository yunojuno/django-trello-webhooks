from django import template

register = template.Library()


@register.filter
def is_image(value):
    """Confirm if attachment is an image inside a template.

    Args:
        value: string, result of getting a mime type of the attachment file

    Returns: bool, True if attachment's mime type is an image, False otherwise.

    """
    if value:
        attachment_spec = value.split("/")
        return attachment_spec[0] == "image"
    else:
        return False
