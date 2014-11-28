# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as date_format
from django.utils.html import format_html

from trello_webhooks.models import Webhook, CallbackEvent
from trello_webhooks.forms import WebhookForm

logger = logging.getLogger(__name__)


class CallbackEventAdmin(admin.ModelAdmin):

    list_display = (
        'timestamp',
        'webhook_',
        'member_',
        'board_',
        'list_',
        'card_',
        'event_type',
    )
    list_filter = (
        'timestamp',
        'event_type'
    )
    fields = (
        'timestamp',
        'webhook',
        'event_type',
        'event_payload',
    )
    readonly_fields = (
        'timestamp',
        'webhook',
        'event_type',
        'event_payload',
    )

    def webhook_(self, instance):
        return instance.webhook.id


class CallbackEventInline(admin.TabularInline):
    model = CallbackEvent
    extra = 0
    fields = (
        'admin_link',
        'timestamp_',
        'action_taken_by',
        'event_type',
        'board_',
        'list_',
        'card_',
    )
    readonly_fields = (
        'timestamp_',
        'event_type',
        'admin_link',
        'action_taken_by',
        'board_',
        'list_',
        'card_',
    )
    ordering = ('-id',)

    def action_taken_by(self, instance):
        return instance.member.get('fullName')

    def timestamp_(self, instance):
        return date_format(instance.timestamp, settings.DATETIME_FORMAT)

    def admin_link(self, instance):
        url = reverse(
            'admin:%s_%s_change' % (
                instance._meta.app_label,
                instance._meta.module_name
            ),
            args=(instance.id,)
        )
        return format_html(
            u'<a href="{}">Edit</a>',
            url
        )


class WebhookAdmin(admin.ModelAdmin):

    inlines = [CallbackEventInline]
    list_display = (
        'description',
        'trello_model_id',
        'has_trello_id',
        'created_at',
        'last_updated_at',
    )
    readonly_fields = (
        'trello_id',
        'created_at',
        'last_updated_at',
    )
    form = WebhookForm

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
