# -*- coding: utf-8 -*-
import json
import logging

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as date_format
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatewords, truncatechars

from trello_webhooks.models import Webhook, CallbackEvent
from trello_webhooks.forms import WebhookForm

logger = logging.getLogger(__name__)


class CallbackEventAdmin(admin.ModelAdmin):

    list_display = (
        'timestamp',
        'webhook_',
        'event_type',
        'has_template',
        'member_name',
        'board_',
        'list_',
        'card_',
    )
    list_filter = (
        'timestamp',
        'event_type'
    )
    fields = (
        'timestamp',
        'webhook',
        'event_type',
        'rendered',
        'payload_',
    )
    readonly_fields = (
        'timestamp',
        'webhook',
        'event_type',
        'rendered',
        'payload_',
    )

    def webhook_(self, instance):
        return instance.webhook.id

    def payload_(self, instance):
        """Returns a prettier version of the payload.

        Take the event_payload JSON, indent it, order the keys and then
        present it as a <code> block. That's about as good as we can get
        until someone builds a custom syntax function.

        """
        pretty = json.dumps(
            instance.event_payload,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
        return mark_safe("<code>%s</code>" % pretty.replace(" ", "&nbsp;"))

    def board_(self, instance):
        return truncatewords(instance.board_name, 3)

    def list_(self, instance):
        return truncatewords(instance.list_name, 3)

    def card_(self, instance):
        return truncatewords(instance.card_name, 3)

    def rendered(self, instance):
        return instance.render()

    def has_template(self, instance):
        return instance.render() is not None


class CallbackEventInline(admin.StackedInline):
    model = CallbackEvent
    extra = 0
    fields = (
        'timestamp_',
        'action_taken_by',
        'event_type',
        'rendered'
    )
    readonly_fields = (
        'timestamp_',
        'event_type',
        'action_taken_by',
        'board_name',
        'list_name',
        'card_name',
        'rendered'
    )
    ordering = ('-id',)

    def action_taken_by(self, instance):
        return instance.member.get('fullName')

    def timestamp_(self, instance):
        url = reverse(
            'admin:%s_%s_change' % (
                instance._meta.app_label,
                instance._meta.module_name
            ),
            args=(instance.id,)
        )
        return format_html(
            u'<a href="{}">{}</a>',
            url, date_format(instance.timestamp, settings.DATETIME_FORMAT)
        )

    def rendered(self, instance):
        return instance.render()


class WebhookAdmin(admin.ModelAdmin):

    # disable for now - may overload system by loading
    # every callback on a single page.
    # inlines = [CallbackEventInline]

    list_display = (
        'auth_token_',
        'description',
        'trello_model_id',
        'trello_id',
        'is_active',
        'created_at',
        'last_updated_at',
    )
    readonly_fields = (
        'trello_id',
        'created_at',
        'last_updated_at',
    )
    form = WebhookForm

    def auth_token_(self, instance):
        return truncatechars(instance.auth_token, 12)

    def sync(self, request, queryset):
        """Sync objects selected to Trello."""
        count = queryset.count()
        if count == 0:
            return

        for hook in queryset:
            hook.sync()
        logger.info(
            u"%s synced %i Webhooks from the admin site.",
            request.user, count
        )

    sync.short_description = "Sync with Trello"
    actions = [sync]

admin.site.register(CallbackEvent, CallbackEventAdmin)
admin.site.register(Webhook, WebhookAdmin)
