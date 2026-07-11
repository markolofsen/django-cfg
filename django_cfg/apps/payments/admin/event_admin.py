"""
PaymentEvent Admin Configuration

Admin interface for the PaymentEvent model (webhook log) using django_cfg.

Fully read-only: rows are written by the webhook view / replay command only.
Reprocess a stored event with ``payments_replay_webhook <event_id>``.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig,
    DateTimeField,
    DocumentationConfig,
    FieldsetConfig,
    ForeignKeyField,
    TextField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from django_cfg.apps.payments.models import PaymentEvent


# ========== ADMIN CONFIG ==========
payment_event_admin_config = AdminConfig(
    model=PaymentEvent,

    # ========== PERFORMANCE ==========
    select_related=["payment"],

    # ========== LIST VIEW ==========
    list_display=[
        "event_id",
        "event_type",
        "provider",
        "payment",
        "received_at",
        "processed_at",
        "error",
    ],

    # ========== DISPLAY FIELDS ==========
    display_fields=[
        TextField(
            name="event_id",
            title="Event",
            monospace=True,
            truncate=32,
        ),
        TextField(
            name="event_type",
            title="Type",
        ),
        TextField(
            name="provider",
            title="Provider",
        ),
        ForeignKeyField(
            name="payment",
            title="Payment",
            display_field="short_id",
            link_to_admin=True,
        ),
        DateTimeField(
            name="received_at",
            title="Received",
            ordering="received_at",
            show_relative=True,
        ),
        DateTimeField(
            name="processed_at",
            title="Processed",
            show_relative=True,
        ),
        # Empty when handling succeeded; the error text (truncated) when it raised.
        TextField(
            name="error",
            title="Error",
            truncate=48,
        ),
    ],

    # ========== LIST OPTIONS ==========
    list_filter=["provider", "event_type", "received_at"],
    search_fields=["event_id", "payment__short_id"],
    ordering=["-received_at"],
    date_hierarchy="received_at",

    # ========== FORM OPTIONS ==========
    readonly_fields=[
        "id",
        "provider",
        "event_id",
        "event_type",
        "payment",
        "payload",
        "received_at",
        "processed_at",
        "error",
    ],

    # ========== FIELDSETS ==========
    fieldsets=[
        FieldsetConfig(
            title="Event",
            fields=["id", "provider", "event_id", "event_type", "payment"],
        ),
        FieldsetConfig(
            title="Processing",
            fields=["received_at", "processed_at", "error"],
        ),
        FieldsetConfig(
            title="Payload",
            fields=["payload"],
            collapsed=True,
        ),
    ],

    # ========== DOCUMENTATION ==========
    documentation=DocumentationConfig(
        source_dir="apps/payments/@docs",
        title="Payments Documentation",
        show_management_commands=False,
        enable_plugins=True,
    ),
)


@admin.register(PaymentEvent)
class PaymentEventAdmin(PydanticAdmin):
    """Admin for the PaymentEvent webhook log (read-only)."""

    config = payment_event_admin_config

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # The event log is the webhook idempotency guard — never prune by hand.
        return False
