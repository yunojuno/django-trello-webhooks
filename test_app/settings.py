# -*- coding: utf-8 -*-
from os import environ, path

import dj_database_url

from django.core.exceptions import ImproperlyConfigured

# ============= APP SETTINGS =====================
MANDATORY_ENVIRONMENT_SETTINGS = (
    'TRELLO_API_KEY',
    'TRELLO_API_SECRET',
    'CALLBACK_DOMAIN',
    'DATABASE_URL'
)
for s in MANDATORY_ENVIRONMENT_SETTINGS:
    if s not in environ:
        raise ImproperlyConfigured(u"Missing environment variable: '%s'" % s)
# ------------------------------------------------
TRELLO_API_KEY = environ['TRELLO_API_KEY']
TRELLO_API_SECRET = environ['TRELLO_API_SECRET']
CALLBACK_DOMAIN = environ['CALLBACK_DOMAIN']
# optional for the test app to send updates to HipChat
HIPCHAT_API_TOKEN = environ.get('HIPCHAT_API_TOKEN', None)
HIPCHAT_ROOM_ID = environ.get('HIPCHAT_ROOM_ID', None)
HIPCHAT_ENABLED = HIPCHAT_API_TOKEN and HIPCHAT_ROOM_ID
if HIPCHAT_ENABLED:
    print u"HipChat integration is ENABLED: %s" % HIPCHAT_ROOM_ID
else:
    print u"HipChat integration is DISABLED"
# ============= / APP SETTINGS ===================

DEBUG = environ.get('DEBUG', False)
TEMPLATE_DEBUG = DEBUG

# You should really update this in your app!
# see https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS', '*')

USE_L10N = True
USE_I18N = True
USE_TZ = True
TIMEZONE = 'Europe/London'

DATABASES = {
    # automatically assumes DATABASE_URL env var
    'default': dj_database_url.config()
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'test_app',
    'trello_webhooks',
)

MIDDLEWARE_CLASSES = [
    # default django middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

TEMPLATE_DIRS = (
)

STATIC_URL = "/static/"

PROJECT_ROOT = path.realpath(path.dirname(__file__))
STATIC_ROOT = path.join(PROJECT_ROOT, 'static')

SECRET_KEY = "secret"

# requests can be really noisy, and it uses a bunch of different
# loggers, so use this to turn all requests-related loggers down
REQUESTS_LOGGING_LEVEL = environ.get('REQUESTS_LOGGING_LEVEL', 'WARNING')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',
        },
        'trello_webhooks': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'requests': {
            'handlers': ['console'],
            'level': REQUESTS_LOGGING_LEVEL,
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['console'],
            'level': REQUESTS_LOGGING_LEVEL,
            'propagate': False,
        },
        'oauthlib': {
            'handlers': ['console'],
            'level': REQUESTS_LOGGING_LEVEL,
            'propagate': False,
        },
        'requests_oauthlib': {
            'handlers': ['console'],
            'level': REQUESTS_LOGGING_LEVEL,
            'propagate': False,
        },
    }
}

ROOT_URLCONF = 'test_app.urls'

APPEND_SLASH = True
