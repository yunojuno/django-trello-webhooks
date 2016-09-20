
def mock_trello_sync(webhook, verb):
    """Fake version of the Webhook._trello_sync method.

    This mock requires no direct connection to Trello, and is deterministic,
    so that it can be used in testing.

    It monkey-patches the Webhook object with the 'verb' kwarg, so that you
    can validate that the expected method was called.

    In addition it sets the trello_id property as per the real version.

    """
    webhook.verb = verb
    if verb == 'POST':
        webhook.trello_id = 'NEW_TRELLO_ID'
        webhook.is_active = True
    elif verb == 'DELETE':
        webhook.trello_id = ''
        webhook.is_active = False
    return webhook


def mock_trello_sync_x(webhook, verb):
    """Fake version of the Webhook._trello_sync method that mimics failure.

    This function mimics the result of _trello_sync if Trello responds with
    something other than a 199.

    """
    webhook = mock_trello_sync(webhook, verb)
    webhook.trello_id = ''
    webhook.is_active = False
    return webhook
