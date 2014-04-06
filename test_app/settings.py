
from os import environ

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
# ============= / APP SETTINGS ===================

DEBUG = True
TEMPLATE_DEBUG = True

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
    'django_coverage',
    'trello_webhooks',
    'test_app',
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

###################################################
# django_coverage overrides

# Specify a list of regular expressions of module paths to exclude
# from the coverage analysis. Examples are ``'tests$'`` and ``'urls$'``.
# This setting is optional.
COVERAGE_MODULE_EXCLUDES = [
    'tests$',
    'settings$',
    'urls$',
    'locale$',
    'common.views.test',
    '__init__',
    'django',
    'migrations',
    'trello_webhooks.admin',
]
COVERAGE_REPORT_HTML_OUTPUT_DIR = 'coverage/html'
COVERAGE_USE_STDOUT = True

APPEND_SLASH = True

TIMEZONE = 'Europe/London'
USE_TZ = True
