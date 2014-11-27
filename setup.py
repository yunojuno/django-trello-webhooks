import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-trello-webhooks",
    version="0.1",
    packages=[
        'trello_webhooks',
        'trello_webhooks.management',
        'trello_webhooks.management.commands',
        'trello_webhooks.templatetags',
        'trello_webhooks.tests',
    ],
    install_requires=['django>=1.7.1'],
    include_package_data=True,
    description='Django Trello Webhooks - Trello callback integration for Django.',
    long_description=README,
    url='https://github.com/yunojuno/django-trello-webhooks',
    author='Hugo Rodger-Brown',
    author_email='hugo@yunojuno.com',
    maintainer='Hugo Rodger-Brown',
    maintainer_email='hugo@yunojuno.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
