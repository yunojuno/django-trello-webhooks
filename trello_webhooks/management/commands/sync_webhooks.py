# # -*- coding: utf-8 -*-
# sync webhooks down from Trello
import logging

from django.core.management.base import BaseCommand

from trello_webhooks.models import Webhook

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = u"<token token ...>"
    help = "Sync webhooks locally with those on Trello."

    def handle(self, *args, **options):
        """Sync webhooks between local database and Trello.

        The syncing process is bidirectional - you may have webhooks registered
        with Trello that are not in the local database, and you may also
        webhooks in the local database that are not registered with Trello.

        Webhooks are registered in Trello against a combination of the Trello
        model id and a user token. The `list_hooks` API call requires a user
        token, and this _may_ be supplied as a command option (--token, -t).

        Alternatively, any tokens that are in the local database are also used,
        when calling `list_hooks`.

        The logic works like this:

        1. Sync all local webhooks to Trello
        2. Fetch all remote webhooks, using all available tokens
        3. Save any remote webhooks not already stored locally

        At this point you should have the same webhooks locally and remotely.
        Any further edits (e.g. deletion) can be made from the admin site.

        """
        local_webhooks = Webhook.objects.all()
        for webhook in local_webhooks:
            logger.info(u"Syncing local webhook (%r) to Trello", webhook)
            webhook.sync()

        # set of unique tokens that we know about from local webhooks,
        # combined with those that were passed in from the command args
        tokens = set([w.auth_token for w in local_webhooks] + [a for a in args])

        # used to match webhooks when comparing with remote hooks
        local_match = lambda h: h.id in [w.trello_id for w in local_webhooks]

        if len(tokens) == 0:
            logger.info(u"There are no user tokens with which to check Trello.")  # noqa
            logger.info(u"Usage: sync_webhooks <token token ...>")  # noqa
            return

        logger.info(u"Checking %i Trello user tokens for missing local webhooks", len(tokens))  # noqa
        for token in tokens:
            for hook in Webhook.remote_objects.list_hooks(token):
                if local_match(hook):
                    logger.info(u"Remote webhook (%s) already exists locally", hook)  # noqa
                else:
                    logger.info(u"Remote webhook (%s) does not exist locally", hook)  # noqa
                    Webhook(
                        trello_id=hook.id,
                        trello_model_id=hook.id_model,
                        description=hook.desc,
                        auth_token=hook.token,
                        is_active=hook.active
                    ).save(sync=False)

        local_webhooks = Webhook.objects.all()
        logger.info(u"Sync complete. There are %i webhooks.", local_webhooks.count())
        for webhook in Webhook.objects.all():
            logger.info(u"%s", webhook)
