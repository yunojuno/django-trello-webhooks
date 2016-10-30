import mimetypes

from django.template.loader import render_to_string
from django.template.loader import TemplateDoesNotExist


def get_mimetype(url):
    """Wrap around stdlib mimetypes and returns a value."""
    mime_type = mimetypes.guess_type(url, strict=False)
    if mime_type[0] == None:
        return ('None/None', 'None')
    return mime_type


def get_attachment_type(mtype):
    """Useful for determining a broader category the attachment belongs to."""
    return mtype[0].split('/')[0]


def render_template_for_attachment(attachment):
    """
    Return a template tailored to the attachment
    type to be rendered. Defaults to attachment name.
    """
    mime_type = get_mimetype(attachment['url'])
    attachment_type = get_attachment_type(mime_type)
    attachment_template_name = "trello_webhooks/media/{}.html".format(attachment_type)
    try:
        return render_to_string(attachment_template_name, attachment)
    except TemplateDoesNotExist:
        return attachment['name']
