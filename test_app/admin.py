# -*- coding: utf-8 -*-
from django.contrib import admin

from test_app.models import EventType

def make_active(modeladmin, request, queryset):
    """Make all the EventType objects in the queryset active."""
    queryset.update(is_active=True)
make_active.short_description = "Activate all selected event types"

def make_inactive(modeladmin, request, queryset):
    """Make all the EventType objects in the queryset inactive."""
    queryset.update(is_active=False)
make_inactive.short_description = "Deactivate all selected event types"


class EventTypeAdmin(admin.ModelAdmin):

    list_display = (
        'label',
        'event_count',
        'is_active'
    )
    readonly_fields = (
        'label',
        'event_count'
    )
    actions = (make_active, make_inactive)

admin.site.register(EventType, EventTypeAdmin)
