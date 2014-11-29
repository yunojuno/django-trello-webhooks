# -*- coding: utf-8 -*-
from settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
}

try:
    import django_nose  # noqa
    print u"Enabling django-nose test runner"
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
except ImportError:
    pass

try:
    import coverage  # noqa
    print u"Enabling coverage plugin to nose"
    NOSE_ARGS = [
        '--with-coverage',
        '--cover-package=trello_webhooks',
        '--cover-html',
        '--cover-html-dir=coverage_reports'
    ]
except ImportError:
    print u"Coverage is not enabled"
