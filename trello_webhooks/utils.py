import mimetypes


def get_mimetype(url):
    """Wrap around stdlib mimetypes and returns a value."""
    mime_type = mimetypes.guess_type(url, strict=False)
    return mime_type if mime_type else 'None/None'


def get_attachment_type(mtype):
    """Useful for determining a broader category the attachment belongs to."""
    return mtype.split('/')[0]
