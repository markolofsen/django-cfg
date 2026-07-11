"""
Payment Admin Configuration

Admin interface for the Payment model using django_cfg.

The admin is a VIEWER: everything money/provider-critical is read-only.
Refunds go through the ``payments_refund`` management command (which drives
the provider and lets the webhook record the authoritative state) — never
through an admin edit.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    DocumentationConfig,
    FieldsetConfig,
    Icons,
    TextField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from django_cfg.apps.payments.models import Payment, PaymentEvent


class PaymentEventInline(admin.TabularInline):
    """Read-only webhook events received for this payment."""

    model = PaymentEvent
    extra = 0
    fields = ["event_id", "event_type", "received_at", "processed_at", "error"]
    readonly_fields = ["event_id", "event_type", "received_at", "processed_at", "error"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ========== ADMIN CONFIG ==========
payment_admin_config = AdminConfig(
    model=Payment,

    # ========== PERFORMANCE ==========
    select_related=["owner", "created_by"],

    # ========== LIST VIEW ==========
    list_display=[
        "short_id",
        "owner",
        "amount",
        "currency",
        "status",
        "provider",
        "reference_kind",
        "reference_id",
        "created_at",
    ],

    # ========== DISPLAY FIELDS ==========
    display_fields=[
        TextField(
            name="short_id",
            title="Payment",
            ordering="short_id",
            monospace=True,
        ),
        TextField(
            name="owner",
            title="Owner",
            truncate=24,
        ),
        TextField(
            name="amount",
            title="Amount (minor)",
            ordering="amount",
        ),
        TextField(
            name="currency",
            title="Currency",
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "secondary",
                "processing": "warning",
                "requires_action": "warning",
                "succeeded": "success",
                "failed": "danger",
                "refunded": "info",
                "cancelled": "secondary",
            },
            icon=Icons.PAYMENT,
        ),
        TextField(
            name="provider",
            title="Provider",
        ),
        TextField(
            name="reference_kind",
            title="Ref kind",
        ),
        TextField(
            name="reference_id",
            title="Ref id",
            truncate=24,
            monospace=True,
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at",
            show_relative=True,
        ),
    ],

    # ========== LIST OPTIONS ==========
    list_filter=["status", "provider", "created_at"],
    search_fields=["short_id", "external_id", "idempotency_key"],
    ordering=["-created_at"],
    date_hierarchy="created_at",

    # ========== FORM OPTIONS ==========
    # Viewer stance: the owner/reference seams, provider linkage and all money
    # fields are frozen. Only `status` stays editable (last-resort operator
    # nudge; the normal paths are webhooks + payments_reconcile).
    readonly_fields=[
        "id",
        "short_id",
        "owner",
        "reference_kind",
        "reference_id",
        "created_by",
        "provider",
        "external_id",
        "idempotency_key",
        "amount",
        "currency",
        "amount_refunded",
        "created_at",
        "updated_at",
    ],

    # ========== FIELDSETS ==========
    fieldsets=[
        FieldsetConfig(
            title="Payment",
            fields=["id", "short_id", "owner", "reference_kind", "reference_id", "created_by", "status"],
        ),
        FieldsetConfig(
            title="Provider",
            fields=["provider", "external_id", "idempotency_key"],
        ),
        FieldsetConfig(
            title="Amount",
            fields=["amount", "currency", "amount_refunded"],
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
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


@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    """Admin for the Payment model (read-mostly; refunds via `payments_refund`)."""

    config = payment_admin_config
    inlines = [PaymentEventInline]

    def has_add_permission(self, request):
        # Payments are created by the checkout API, never by hand.
        return False
