import mock
from nose.tools import raises, assert_equal
from trello_webhooks import contenttypes


def make_breaking_function():
    values = {}
    def breaking_(value):
        if value in values:
            raise ValueError("Cannot re-add same value %s" % repr(value))
        values[value] = 1
    return breaking_



@raises(ValueError)
def test_example_of_breakage():
    # the non memoized version raises an error on the second call
    breaking = make_breaking_function()
    breaking(1)
    breaking(1)


def test_memo_calls_once():
    # the memoized version can be called twice with the same value
    breaking = make_breaking_function()
    non_breaking = contenttypes.memo(breaking)
    non_breaking(1)
    non_breaking(1)


def fake_chunk(url):
    return u''


@mock.patch('trello_webhooks.contenttypes.read_chunk', fake_chunk)
def test_get_attachment_content_type():
    mtype = contenttypes.get_attachment_content_type('http://example.com')
    assert_equal(mtype, 'application/x-empty')
