"""
Payment Admin v2.0 - NEW Declarative Pydantic Approach

Clean, modern payment management using Unfold Admin with declarative config.
"""

from django.contrib import admin
from django.utils import timezone

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    CurrencyField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    TextField,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Payment
from .filters import PaymentAmountFilter, PaymentStatusFilter, RecentActivityFilter
from .payment_actions import cancel_payments, mark_as_completed, mark_as_failed

# ✅ Declarative Pydantic Config
payment_config = AdminConfig(
    model=Payment,

    # Performance optimization
    select_related=["user", "currency"],

    # List display
    list_display=[
        "internal_payment_id",
        "user",
        "amount_usd",
        "currency",
        "status",
        "status_changed_at",
        "created_at"
    ],

    # Display fields with NEW specialized classes
    display_fields=[
        BadgeField(
            name="internal_payment_id",
            title="Payment ID",
            variant="info",
            icon=Icons.RECEIPT
        ),
        UserField(
            name="user",
            title="User",
            header=True
        ),
        CurrencyField(
            name="amount_usd",
            title="Amount",
            currency="USD",
            precision=2
        ),
        TextField(
            name="currency",
            title="Currency"
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "confirming": "info",
                "confirmed": "primary",
                "completed": "success",
                "partially_paid": "warning",
                "failed": "danger",
                "cancelled": "secondary",
                "expired": "danger"
            }
        ),
        DateTimeField(
            name="status_changed_at",
            title="Status Changed",
            ordering="status_changed_at",
            empty_value="-"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Filters
    list_filter=[
        PaymentStatusFilter,
        PaymentAmountFilter,
        RecentActivityFilter,
        "currency",
        "created_at",
        "status_changed_at",
    ],

    # Search
    search_fields=[
        "internal_payment_id",
        "provider_payment_id",
        "transaction_hash",
        "user__username",
        "user__email",
        "pay_address"
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "internal_payment_id",
        "provider_payment_id",
        "created_at",
        "updated_at",
        "status_changed_at",
        "completed_at",
        "payment_details_display",
        "qr_code_display",
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["internal_payment_id", "status", "description"]
        ),
        FieldsetConfig(
            title="Payment Details",
            fields=["amount_usd", "currency", "pay_amount", "actual_amount", "actual_amount_usd"]
        ),
        FieldsetConfig(
            title="Provider Information",
            fields=["provider", "provider_payment_id", "pay_address", "payment_url"]
        ),
        FieldsetConfig(
            title="Blockchain Information",
            fields=["transaction_hash", "confirmations_count"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at", "status_changed_at", "completed_at", "expires_at"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Additional Info",
            fields=["provider_data", "payment_details_display", "qr_code_display"],
            collapsed=True
        ),
    ],

    # Actions with direct function references
    actions=[
        ActionConfig(
            name="mark_as_completed",
            description="Mark as completed",
            variant="success",
            handler=mark_as_completed
        ),
        ActionConfig(
            name="mark_as_failed",
            description="Mark as failed",
            variant="danger",
            handler=mark_as_failed
        ),
        ActionConfig(
            name="cancel_payments",
            description="Cancel payments",
            variant="warning",
            handler=cancel_payments
        ),
    ],

    # Ordering
    ordering=["-created_at"],
    list_per_page=50
)


# ✅ Minimal Admin Class with Custom Readonly Methods
@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    """
    Payment admin for Payments v2.0 using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Clean UI with Unfold theme
    - NowPayments-specific status handling
    - Custom readonly fields for detail view
    """
    config = payment_config

    # Custom readonly field methods using self.html
    def payment_details_display(self, obj):
        """Detailed payment information for detail view using self.html."""
        if not obj.pk:
            return "Save to see details"

        # Calculate age
        age = timezone.now() - obj.created_at
        age_text = f"{age.days} days, {age.seconds // 3600} hours"

        # Transaction details
        transaction_value = None
        if obj.transaction_hash:
            explorer_link = obj.get_explorer_link()
            if explorer_link:
                transaction_value = self.html.link(
                    explorer_link,
                    f"{obj.transaction_hash[:16]}...",
                    target="_blank"
                )
            else:
                transaction_value = self.html.code(obj.transaction_hash)

        return self.html.breakdown(
            self.html.key_value("Internal ID", obj.internal_payment_id),
            self.html.key_value("Age", age_text),
            self.html.key_value(
                "Provider Payment ID",
                obj.provider_payment_id
            ) if obj.provider_payment_id else None,
            self.html.key_value(
                "Transaction",
                transaction_value
            ) if obj.transaction_hash else None,
            self.html.key_value(
                "Confirmations",
                self.html.badge(str(obj.confirmations_count), variant="info", icon=Icons.CHECK_CIRCLE)
            ) if obj.confirmations_count > 0 else None,
            self.html.key_value(
                "Pay Address",
                self.html.code(obj.pay_address)
            ) if obj.pay_address else None,
            self.html.key_value(
                "Pay Amount",
                self.html.inline(
                    self.html.number(obj.pay_amount, precision=8),
                    obj.currency.token,
                    separator=" "
                )
            ) if obj.pay_amount else None,
            self.html.key_value(
                "Actual Amount",
                self.html.inline(
                    self.html.number(obj.actual_amount, precision=8),
                    obj.currency.token,
                    separator=" "
                )
            ) if obj.actual_amount else None,
            self.html.key_value(
                "Payment URL",
                self.html.link(obj.payment_url, "Open", target="_blank")
            ) if obj.payment_url else None,
            self.html.key_value(
                "Expired",
                self.html.badge(f"Yes ({obj.expires_at})", variant="danger", icon=Icons.ERROR)
            ) if obj.expires_at and obj.is_expired else (
                self.html.key_value("Expires At", str(obj.expires_at)) if obj.expires_at else None
            ),
            self.html.key_value(
                "Description",
                obj.description
            ) if obj.description else None
        )

    payment_details_display.short_description = "Payment Details"

    def qr_code_display(self, obj):
        """QR code display for payment address using self.html."""
        if not obj.pay_address:
            return self.html.empty()

        qr_url = obj.get_qr_code_url(size=200)
        if qr_url:
            from django.utils.html import format_html
            img_html = format_html('<img src="{}" alt="QR Code" style="max-width:200px;">', qr_url)
            caption = self.html.inline(
                self.html.text("Scan to pay:", size="sm"),
                self.html.code(obj.pay_address),
                separator=" "
            )
            return self.html.breakdown(img_html, caption)
        return self.html.text(f"Address: {obj.pay_address}", size="sm")
