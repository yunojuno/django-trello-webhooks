# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from trello_webhooks.models import Webhook, CallbackEvent
from trello_webhooks.forms import WebhookForm

logger = logging.getLogger(__name__)


class CallbackEventAdmin(admin.ModelAdmin):

    list_display = (
        'timestamp',
        'webhook',
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
        'event_payload'
    )
    readonly_fields = (
        'timestamp',
        'webhook',
        'event_type',
        'event_payload'
    )


class CallbackEventInline(admin.TabularInline):
    model = CallbackEvent
    extra = 0
    fields = (
        'admin_link',
        'event_type',
        'timestamp',
    )
    readonly_fields = (
        'event_type',
        'timestamp',
        'admin_link',
    )
    ordering = ('-id',)

    def admin_link(self, instance):
        url = reverse(
            'admin:%s_%s_change' % (
                instance._meta.app_label,
                instance._meta.module_name
            ),
            args=(instance.id,)
        )
        return format_html(u'<a href="{}">Edit</a>', url)


class WebhookAdmin(admin.ModelAdmin):

    inlines = [CallbackEventInline]
    list_display = (
        'trello_model_id',
        'auth_token',
        'description',
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
