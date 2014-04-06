# Template tags used in BackOffice only
from django import template

from trello_webhooks.settings import TRELLO_API_KEY

register = template.Library()


@register.simple_tag
def trello_api_key():
    """Return TRELLO_API_KEY for use in templates."""
    return TRELLO_API_KEY
