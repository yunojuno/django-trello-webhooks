# -*- coding: utf-8 -*-
from settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
}

try:
    import coverage  # noqa
    import django_coverage  # noqa
    print u"Enabling coverage test runner"
    TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'
    COVERAGE_REPORT_HTML_OUTPUT_DIR = 'coverage_reports'
    COVERAGE_USE_STDOUT = True
    COVERAGE_MODULE_EXCLUDES = [
        'tests$',
        'settings$',
        'urls$',
        'locale$',
        '__init__',  # we need to see code that lives at the top of a module
        # 'django',
        'fixtures',
        'templates',
        'migrations',
        # Above are the defaults, below are YJ-specific extras
        'admin',  # ie, all admin.py files
    ]
except ImportError:
    print u"Coverage is not enabled as missing coverage, django-coverage apps"
