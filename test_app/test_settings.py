# -*- coding: utf-8 -*-
from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
}

try:
    import coverage
    import django_coverage
    TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'

    # django_coverage settings, in case it's enabled in LOCAL_APPS
    COVERAGE_REPORT_HTML_OUTPUT_DIR = path.join('coverage_reports')
    COVERAGE_USE_STDOUT = True

    COVERAGE_MODULE_EXCLUDES = [
        'tests$',
        'settings$',
        '^urls$',
        'urls',
        'locale$',
        # '__init__',  # we need to see code that lives at the top of a module
        'django',
        'fixtures',
        'templates',
        'migrations',
        # Above are the defaults, below are YJ-specific extras
        'admin',  # ie, all admin.py files
    ]
except ImportError:
    print u"Coverage is not enabled as missing coverage, django-coverage apps"
