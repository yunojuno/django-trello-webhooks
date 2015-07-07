import magic
import requests
from functools import wraps

# https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#Supported_image_formats
known_extensions = {
    'image/jpeg': 'jpg',
    'image/gif': 'gif',
    'image/png': 'png',
    'image/bmp': 'bmp',
    'image/x-windows-bmp': 'bmp',
    'image/svg+xml': 'svg',
    'image/x-icon': 'ico',
}


def memo(func):
    cache = {}
    @wraps(func)
    def wrap(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrap


def read_chunk(url):
    """Returns the 1st 1024 bytes of a given url

    This is typically enough to determine the mimetype of a given file"""
    rsp = requests.get(url, stream=True)
    return next(rsp.iter_content(1024))


# is it a safe assumption that an attachment url cannot be overwritten and
# so we do not need to check the same url more than once?
@memo
def get_attachment_content_type(url):
    return magic.from_buffer(read_chunk(url), mime=True)


def attachment_is_image(url):
    return get_attachment_content_type(url) in known_extensions


def merge_content_type(attachment):
    """If applicable, update attachment with the attachment contenttype"""
    try:
        ctype = get_attachment_content_type(attachment['previewUrl'])
    except (TypeError, KeyError):
        ctype = u''
    if ctype and attachment:
        attachment['contentType'] = ctype
    return attachment
