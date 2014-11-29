# -*- coding: utf-8 -*-
from settings import *  # noqa

HIPCHAT_ENABLED = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
}

# the django apps aren't required for the tests,
INSTALLED_APPS = ('trello_webhooks',)

try:
    import django_nose  # noqa
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    print u"TEST_RUNNER set to use django_nose"
    import coverage  # noqa
    print u"TEST_RUNNER config includes coverage"
    NOSE_ARGS = [
        '--with-coverage',
        '--cover-package=trello_webhooks',
        '--cover-html',
        '--cover-html-dir=coverage_reports'
    ]
except ImportError:
    pass
