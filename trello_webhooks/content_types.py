import logging
import mimetypes

import requests


logger = logging.getLogger(__name__)


def request_content_type(url):
    """Get the url content-type using a HEAD http request."""
    try:
        resp = requests.head(url)
    except requests.RequestException:
        logger.exception("Unable to fetch attachment content-type")
    else:
        return resp.headers.get('content-type')


def guess_url_content_type(url):
    """Return the content-type of a url

    This is by means of inspecting the extension or headers.
    """
    guessed_type = mimetypes.guess_type(url)[0]
    if not guessed_type:
        guessed_type = request_content_type(url)
    return guessed_type


def is_image(content_type):
    """Check if a content-type is an image."""
    return content_type.startswith('image')
