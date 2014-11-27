django-trello-webhooks
======================

Django application for managing Trello webhooks.

**\*LOOKING FOR CONTRIBUTORS\***

Status
------

It lives!

The app currently works (on my machine) - so is really now at the "proof of concept"
stage. I haven't packaged it properly, there are no tests (none at all), but
it does really work.

Background
----------

`Trello webhooks <https://trello.com/docs/gettingstarted/webhooks.html>`_
can only be managed programmatically via the API, which is clever, but also
a massive PITA. In addition, whilst creating a new webhook, Trello will
immediately call the registered callback URL with a HEAD request to verify
that it exists. This makes setting up webhooks fiddly and complex (esp. when
experimenting in a local development environment).

This project is a Django app that makes managing Trello webhook easy. Well,
easier. It exposes Trello webhooks through the Django admin site as standard
Django models that can be created and deleted through a web UI. Incoming
webhook events are then exposed via Django signals that are raised, and
can be integrated into your application.

How does it work?
-----------------

Each webhook is modelled as a Django model (``Webhook``), and each callback
received on the webhook is modelled as a ``CallbackEvent`` object that
contains the JSON payload (so it will maintain a complete history of all
callbacks).

The ``Webhook.save()`` method is used to register the webhook with the Trello
API. The corresponding delete method is used to delete the webhook from Trello.

The app contains a single view function, ``api_callback``, which receives the
callback from Trello, and which also supports the synchronous activation of
new webhooks by Trello. (When you create a webhook via the Trello API, they
will immediately issue a HEAD request to the callback url supplied, so you
need to be able to handle this immediately.)

The important bit is then how you use the callback in your application.
This is done via Django signals. On each webhook callback, the app sends the
``callback_received`` signal, passing in the data received via the callback.

Your application then connects via this signal:

.. code:: python

    from django.dispatch import receiver
    
    from trello_webhooks.signals import callback_received
    
    @receiver(callback_received, dispatch_uid="callback_received")
    def on_callback_received(sender, **kwargs):
        event = kwargs.pop('event')
        print "This is the event payload: ", event.event_payload

There is a Django management command which can be used to synchronise any
existing webhooks (in both directions), called ``sync_webhooks``. Run on
its own, without any arguments, this will look up all the webhooks in
the local Django database, and sync then with Trello (creating them if
they don't already exist). It will also check Trello for any webhooks
that it has registered that do not exist locally, and create them.

Configuration
-------------

There are three mandatory environment settings (following the 
`12-factor app <http://12factor.net/>`_ principal):

* TRELLO_API_KEY
* TRELLO_API_SECRET
* CALLBACK_DOMAIN

The first two are the core Trello developer API keys - available from here:
https://trello.com/1/appKey/generate

The CALLBACK_DOMAIN is included as you need to give a fully-qualified domain
to the Trello API, and it's not always possible to infer what that might be
- for instance when developing locally, you will need a tunnel from your
machine out onto the web using something like `ngrok <https://ngrok.com/>`_.

When managing hooks via the Trello API a third key is required, and this is
user specific - the admin site has a link next to the `auth_token` field on
the form for creating a new Webhook. This uses the Trello API client.js to
perform the Oauth dance - and supplies the user token. All webhooks are
registered against a user token. That's how it works. (NB you can pass any
user tokens you have lying around to the ``sync_webhooks`` command and it
will check Trello for any existing webhooks registered with those tokens.)

Tests
-----

Ahem, there aren't any at the moment. 0% coverage, use at your own risk.
(I will get round to it at some point.)

Setup
-----

The app is available on PyPI as ``django-trello-webhooks``, so install with ``pip``:

.. code:: shell
    
    $ pip install django-trello-webhooks

Further Developments
--------------------

* Write some tests
* Better integration with the Trello API
* Handle user auth token expiry properly
* Integration with Heroku's "Deploy to Heroku" button

Contributing
------------

Usual rules apply - fork, send pull request. Please try and adhere to the existing
coding style - it may not be your style, but it's the project's style, so PRs will
be rejected if they 'smell bad'. Specifically, given that this is an app that is
pushing data over the wire, and therefore hard to debug - lots of logging, and
lots of comments. Seriously. Lots.

Licence
-------

MIT (see LICENCE file)

Dependencies
------------

The core Trello API integration is done using `py-trello <https://github.com/sarumont/py-trello>`_
from Richard Kolkovich (@sarumont), so thanks to him for that. He naturally
relies on `requests <http://docs.python-requests.org/en/latest/>`_ from Kenneth Reitz,
as well as `request-oauthlib <https://requests-oauthlib.readthedocs.org/en/latest/>`_, so
thanks to anyone involved with either of those.


Addenda
-------

The webhook API works on the concept of a Trello model id. This refers to the object
being watched - and could be a Board, a List, a Card etc. Getting these ids is a bit
of a pain, to put it mildly, so I would strongly recommend using the excellent
`Trello Explorer <http://www.hwartig.com/trelloapiexplorer>`_ app from Harald Wartig (@hwartig).

I would also recommend the use of `ngrok <https://ngrok.com/>`_ to expose your local
Django dev server during development.

As for development itself - use virtualenv, install dependencies from requirements.txt
and set up environment variables. If that doesn't mean anything to you - I'm afraid
you have a lot to learn.
