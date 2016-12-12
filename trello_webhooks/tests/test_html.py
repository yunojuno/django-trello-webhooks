import collections
from django.template.loader import render_to_string
from nose.tools import assert_true


def vivify():
    return collections.defaultdict(vivify)


def test_rendering():
    att = {'contentType': 'image/png', u'url': u'https://foo.com', 'name': u'FOO'}
    context = vivify()
    context['action']['data']['attachment'] = att
    context['action']['memberCreator']['initials'] = u'RJS'
    template = 'trello_webhooks/addAttachmentToCard.html'
    html = render_to_string(template, context).strip()
    expected = u'<strong>RJS</strong> added attachment "<strong> <a href="https://foo.com"><img src="https://foo.com"></a> </strong>"'
    assert_true(html.startswith(expected))
