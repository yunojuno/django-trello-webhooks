django-trello-webhooks
======================

Django application for managing Trello webhooks.

**\*LOOKING FOR CONTRIBUTORS\***

Status
------

.. image:: https://travis-ci.org/yunojuno/django-trello-webhooks.svg?branch=master
    :target: https://travis-ci.org/yunojuno/django-trello-webhooks

The app is now working, and deployable to Heroku (see below). The main outstanding
issue is writing some proper docs, but until / unless there is any genuine external
interest shown in this project I won't be spending any formal time on it, so
please don't expect much more.

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

Your application then connects via this signal; below is taken from the
included test_app, which sends the formatted event to HipChat:

.. code:: python

    from django.conf import settings
    from django.dispatch import receiver

    from test_app.hipchat import send_to_hipchat
    
    from trello_webhooks.signals import callback_received
    
    @receiver(callback_received, dispatch_uid="callback_received")
    def on_callback_received(sender, **kwargs):
    if settings.HIPCHAT_ENABLED:
        event = kwargs.pop('event')
        send_to_hipchat(event.render())
        
If you wanted to filter out only certain events for sending:

.. code:: python

    def on_callback_received(sender, **kwargs):
        event = kwargs.pop('event')
        if event.event_type == 'commentCard':
            send_to_hipchat(event.render())

There is a Django management command which can be used to synchronise any
existing webhooks (in both directions), called ``sync_webhooks``. Run on
its own, without any arguments, this will look up all the webhooks in
the local Django database, and sync then with Trello (creating them if
they don't already exist). It will also check Trello for any webhooks
that it has registered that do not exist locally, and create them.

Rendering the payload
~~~~~~~~~~~~~~~~~~~~~

Once you've received a callback, along with its JSON payload, the next
question is how to use it effectively. It is assumed (by me) that the
core use case for this project is to pipe the events elsewhere - in
our case it's to HipChat, but other messaging services are available - 
you've could even go old-school and email people stuff. Whatever you
decide to do, you will probably want to convert the JSON into some
form of readable text output. In order to facilitate this each event
type (``createCard``, ``commentCard`` etc.) has an associated Django
template. The ``CallbackEvent`` model has a ``render`` method that
passes the entire JSON payload into the relevant template as the
template context, so that you can extract the data.

Below is an example of the default ``commendCard.html`` template.

.. code:: html

    <b>{{action.memberCreator.fullName}}</b> commented
    on the card "<b>{{action.data.card.name}}</b>"
    on the board "<b>{{action.data.board.name}}</b>":
    <blockquote>{{action.data.text}}</blockquote>
    
The default templates are designed to show what is possible - and it's
recommended that you override these in your application. You can do
this using simple Django template overriding - simply add your template
to your application in the same locaion (``/templates/trello_webhooks/<event_type>.html``)
and declare your app **above** the ``trello_webhooks`` app in the
``INSTALLED_APPS`` setting, and your template will be used instead
of the default.

The combination of overrideable templates and the ``callback_received`` signal
mean that you should be able to integrate Trello fully into your app.

**NB One word of caution**

I have made no attempt to ensure that all events are covered - that's not
really the point. This app will store and forward any event that it
receives. In order to make it a little easier to manage unexpected events
there is a property of the ``CallbackEvent`` that is displayed in the
admin site list view - **Has Template**. If this is True, then this is
an event for which we have a default template. If it's False, then
this is a new one on us - and you are encouraged to play around with
adding a new template. Do please feed all new default templates back
to the project.

Configuration
-------------

There are three mandatory environment settings (following the 
`12-factor app <http://12factor.net/>`_ principle):

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

Deploying to Heroku
-------------------

TODO: write proper docs

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy?template=https://github.com/yunojuno/django-trello-webhooks

This repo contains a test app can be deployed directly to Heroku using their Deploy button.
This app will pipe Trello updates directly to a Hipchat room. You will need the following
information in order to set up and configure the app:

``TRELLO_API_KEY``, ``TRELLO_API_SECRET``, which you can get from here - https://trello.com/1/appKey/generate
``HIPCHAT_API_TOKEN``, ``HIPCHAT_ROOM_ID``, which you can get from hipchat.com

In addition, you will need to set the ``CALLBACK_DOMAIN`` environment setting once the app
has been deployed. This should be set to the <app_name>.herokuapp.com domain, that is
available once Heroku has deployed it.

The recommended hacking method (IMO) is to set up the Heroku app, and use that as your
main git remote - pull it down locally, change the relevant templates, push back to
Heroku. If you're actually adding functionality, then please follow the **contributing**
instructions above.
