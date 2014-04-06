django-trello-webhooks
======================

Django application for managing Trello webhooks.

**\*LOOKING FOR CONTRIBUTORS\***

Background
----------

`Trello webhooks <https://trello.com/docs/gettingstarted/webhooks.html>`_
can only be managed programmatically via the API,
which is clever, but also a massive PITA. In addition, whilst
creating a new webhook, Trello will immediately call the registered
callback URL with a HEAD request to verify that it exists. This makes
setting up webhooks fiddly and complex (esp. when experimenting in
a local development environment).

Proposed solution
-----------------

This app adds Trello webhook management to a Django project.
The proposal is that each webhook is modelled as a Django model,
which would create the webhook on ``Webhook.save()``, and handle all of the
callback processing without the user having to specify a URL. The
creation process would therefore work like this:

1. Create new webhook in Django admin
2. Django saves model to database (id is generated), marks as inactive
3. Django calls Trello, supplying default callback (``/webhooks/<webhook_id>``)
4. Trello calls Django on supplied callback URL (``/webhooks/<webhook_id>``)
5. Django marks webhook as active, returns 200, Trello activates webhook

The app itself would do nothing other than manage the Trello interaction,
handle incoming webhook calls. It might log the number of webhook calls
just for reference (num_callbacks, last_callback_at timestamp etc.)

The important bit is then how you use the callback in your application.
This would be done via Django signals. On each webhook callback, the app
will send the ``webhook_callback_received`` signal, passing in the data
received via the callback, deserialized from the JSON into python objects
(using `py-trello <https://github.com/sarumont/py-trello>`_ or equivalent).
Your application then connects via this signal:

.. code:: python

    from django.dispatch import receiver
    from trello_webhooks.signals import webhook_callback_received

    @receiver(webhook_callback_received)
    def on_webhook_callback_received(sender, **kwargs):
        """Handle calback from Trello webhook."""
        action = kwargs['action']
        model = kwargs['model']
        print (
            u"Callback received for '%s' action on model '%s'" %
            (action['type'], model['name'])
        )

On setup, an initial ``sync_webhooks`` management command would query
the Trello API for any existing webhooks. Trello automaticall removes
webhooks that fail to respond with a 200, so if any do exist, they are
clearly being processed somewhere. The management command would offer
the user the choice of leaving the webhook as-is, or of transferring it
to the app, in which case a model would be added, and Trello would be
updated to use the new app callback URL.

Subsequent ``save`` and ``delete`` operations would call the API.

.. code:: shell

    # assume Trello has 'test1', 'test2'
    $ python manage.py sync_webhooks

    Fetching webhooks from Trello...

    - Found 2 webhooks registered with Trello:

    Webhook "test1" currently points to "https://foobar.com/1"; would you like to take this over? [Y/n] Y

    - Adding webhook "test1" to Django

    Webhook "test2" currently points to "https://baz.com/2"; would you like to take this over? [Y/n] n

    - Ignoring webhook "test2"

    Webhook sync complete:

    - 1 existing webhook has been added to Django
    - 1 existing webhook has been ignored

    Django and Trello are now synchronised; please use the Django admin site to manage your webhooks.

    $

Requirements
------------

1. Model Trello webhooks as Django models
2. List all existing webhooks
3. Add new webhooks via Django admin
4. Delete webhooks via Django admin
5. Sync webhooks with models (Trello -> Django)
6. Sync models with webhooks (Django -> Trello)
7. Pluggable backends for processing webhook events
