import mimetypes

from django import template

register = template.Library()


@register.filter
def is_image(url):
    """Check the content-type for `url`. Returns `True` if it's an image
    or `False` if can't be guessed or isn't an image.

    """
    # The first element is the content-type
    contenttype = mimetypes.guess_type(url)[0]
    if contenttype is not None and contenttype.startswith('image/'):
        return True
    return False
