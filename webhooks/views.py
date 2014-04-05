# callback views.
# import datetime
import logging
# import HTMLParser
# from django.conf import settings
# from django.db import transaction, DatabaseError
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponseForbidden
)
from django.shortcuts import get_object_or_404
# from django.template.loader import render_to_string
# from django.template.context import RequestContext
# from django.views.decorators.http import require_POST
# from django.utils.html import strip_tags
# from django.contrib.auth.decorators import user_passes_test
# from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
# from django.views.decorators.cache import never_cache
# from django.forms import ValidationError
# from django.utils.safestring import mark_safe

# from django_fsm.db.fields.fsmfield import TransitionNotAllowed

logger = logging.getLogger(__name__)


def api_callback(request, webhook_id):
    """Handle the callback from Trello."""
    logger.debug(u"Callback from Trello on Webhook %s:\n%s", webhook_id, request)
    return HttpResponse()