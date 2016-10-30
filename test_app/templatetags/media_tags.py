from trello_webhooks.templatetags.trello_webhook_tags import register
from trello_webhooks.utils import render_template_for_attachment


@register.filter
def render_media(attachment):
    """
    Return a rendered html template tailored to a
    specific attachment type.
    """
    return render_template_for_attachment(attachment)
