# Template tags used in BackOffice only
from django import template

from trello_webhooks.settings import TRELLO_API_KEY

register = template.Library()


@register.simple_tag
def trello_api_key():
    """Return TRELLO_API_KEY for use in templates."""
    return TRELLO_API_KEY


@register.filter
def trello_updates(new, old):
    """Parse out the updates from Trello payload.

    Best explained by an example: when a list is moved, an updateList
    event is fired, and the payload from Trello contains the following
    in the action.data node:

    {
        "list":{
            "id": "5476fc06d998c88c890b901d",
            "pos": 131071,
            "name": "Second list"
        },
        "old":{
            "pos": 262143
        }
    }

    From this, we can work out that the field that has changed is 'pos',
    as it's in the 'old' dict, and that its value has changed from
    262143 to 131071

    The output from this tag would therefore be:

    {"pos": (262143, 131071)}

    Args:
        new: dict, the complete node in its current state
        old: dict, the 'old' node against which to compare

    Returns: a dictionary containing the fields that have
        changed as the keys, and a 2-tuple as the value
        containing old, new values of the field.

    """
    try:
        return {k: (v, new[k]) for k, v in old.iteritems()}
    except KeyError:
        return {k: (v, None) for k, v in old.iteritems()}
