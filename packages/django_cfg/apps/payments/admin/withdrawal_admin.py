"""
Withdrawal Admin v2.0 - NEW Declarative Pydantic Approach

Manual approval workflow for withdrawal requests with clean declarative config.
"""

from django.contrib import admin

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
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import WithdrawalRequest
from .filters import RecentActivityFilter, WithdrawalStatusFilter
from .withdrawal_actions import approve_withdrawals, mark_as_completed, reject_withdrawals


# ===== WithdrawalRequest Admin =====

withdrawalrequest_config = AdminConfig(
    model=WithdrawalRequest,

    # Performance optimization
    select_related=["user", "currency", "admin_user"],

    # List display
    list_display=[
        "withdrawal_id",
        "user",
        "amount_usd",
        "currency",
        "status",
        "admin_user",
        "created_at"
    ],

    # Display fields with NEW specialized classes
    display_fields=[
        BadgeField(
            name="withdrawal_id",
            title="Withdrawal ID",
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
            precision=2,
            ordering="amount_usd"
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
                "approved": "info",
                "processing": "primary",
                "completed": "success",
                "rejected": "danger",
                "cancelled": "secondary"
            },
            ordering="status"
        ),
        TextField(
            name="admin_user",
            title="Admin",
            empty_value="—"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Filters and search
    list_filter=[
        WithdrawalStatusFilter,
        RecentActivityFilter,
        "currency",
        "status",
        "created_at"
    ],

    search_fields=[
        "id",
        "internal_withdrawal_id",
        "user__username",
        "user__email",
        "wallet_address",
        "admin_user__username"
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "internal_withdrawal_id",
        "created_at",
        "updated_at",
        "approved_at",
        "completed_at",
        "rejected_at",
        "cancelled_at",
        "status_changed_at",
        "withdrawal_details_display"
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Request Information",
            fields=[
                "id",
                "internal_withdrawal_id",
                "user",
                "status",
                "amount_usd",
                "currency",
                "wallet_address"
            ]
        ),
        FieldsetConfig(
            title="Fee Calculation",
            fields=[
                "network_fee_usd",
                "service_fee_usd",
                "total_fee_usd",
                "final_amount_usd"
            ],
            collapsed=True
        ),
        FieldsetConfig(
            title="Admin Actions",
            fields=[
                "admin_user",
                "admin_notes"
            ]
        ),
        FieldsetConfig(
            title="Transaction Details",
            fields=[
                "transaction_hash",
                "crypto_amount"
            ],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=[
                "created_at",
                "updated_at",
                "approved_at",
                "completed_at",
                "rejected_at",
                "cancelled_at",
                "status_changed_at"
            ],
            collapsed=True
        ),
        FieldsetConfig(
            title="Withdrawal Details",
            fields=["withdrawal_details_display"],
            collapsed=True
        )
    ],

    # Actions with direct function references
    actions=[
        ActionConfig(
            name="approve_withdrawals",
            description="Approve withdrawals",
            variant="success",
            handler=approve_withdrawals
        ),
        ActionConfig(
            name="reject_withdrawals",
            description="Reject withdrawals",
            variant="danger",
            handler=reject_withdrawals
        ),
        ActionConfig(
            name="mark_as_completed",
            description="Mark as completed",
            variant="success",
            handler=mark_as_completed
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(PydanticAdmin):
    """
    Withdrawal Request admin for Payments v2.0 using NEW Pydantic declarative approach.

    Features:
    - Manual approval workflow
    - Admin tracking
    - Status management
    - Clean declarative config
    """
    config = withdrawalrequest_config

    # Custom display methods using decorators
    @computed_field("Withdrawal ID")
    def withdrawal_id(self, obj):
        """Withdrawal ID display with badge."""
        # Show internal_withdrawal_id if available, otherwise use UUID
        withdrawal_id = obj.internal_withdrawal_id if obj.internal_withdrawal_id else str(obj.id)[:16]
        return self.html.badge(withdrawal_id, variant="info")

    @computed_field("Currency")
    def currency(self, obj):
        """Currency display with token+network."""
        if not obj.currency:
            return self.html.badge("N/A", variant="secondary")

        # Display token and network
        text = obj.currency.token
        if obj.currency.network:
            text += f" ({obj.currency.network})"

        return self.html.badge(text, variant="primary", icon=Icons.CURRENCY_BITCOIN)

    # Readonly field displays using self.html
    def withdrawal_details_display(self, obj):
        """Detailed withdrawal information for detail view using self.html."""
        if not obj.pk:
            return "Save to see details"

        # Build details list
        details = []

        details.append(self.html.inline([
            self.html.span("Withdrawal ID:", "font-semibold"),
            self.html.span(str(obj.id), "")
        ], separator=" "))

        details.append(self.html.inline([
            self.html.span("User:", "font-semibold"),
            self.html.span(f"{obj.user.username} ({obj.user.email})", "")
        ], separator=" "))

        details.append(self.html.inline([
            self.html.span("Amount:", "font-semibold"),
            self.html.span(f"${obj.amount_usd:.2f} USD", "")
        ], separator=" "))

        details.append(self.html.inline([
            self.html.span("Currency:", "font-semibold"),
            self.html.span(obj.currency.code, "")
        ], separator=" "))

        details.append(self.html.inline([
            self.html.span("Wallet Address:", "font-semibold"),
            self.html.span(f"<code>{obj.wallet_address}</code>", "")
        ], separator=" "))

        details.append(self.html.inline([
            self.html.span("Status:", "font-semibold"),
            self.html.span(obj.get_status_display(), "")
        ], separator=" "))

        if obj.network_fee_usd:
            details.append(self.html.inline([
                self.html.span("Network Fee:", "font-semibold"),
                self.html.span(f"${obj.network_fee_usd:.2f} USD", "")
            ], separator=" "))

        if obj.service_fee_usd:
            details.append(self.html.inline([
                self.html.span("Service Fee:", "font-semibold"),
                self.html.span(f"${obj.service_fee_usd:.2f} USD", "")
            ], separator=" "))

        if obj.total_fee_usd:
            details.append(self.html.inline([
                self.html.span("Total Fee:", "font-semibold"),
                self.html.span(f"${obj.total_fee_usd:.2f} USD", "")
            ], separator=" "))

        if obj.final_amount_usd:
            details.append(self.html.inline([
                self.html.span("Final Amount:", "font-semibold"),
                self.html.span(f"${obj.final_amount_usd:.2f} USD", "")
            ], separator=" "))

        if obj.admin_user:
            details.append(self.html.inline([
                self.html.span("Approved By:", "font-semibold"),
                self.html.span(obj.admin_user.username, "")
            ], separator=" "))

        if obj.admin_notes:
            details.append(self.html.inline([
                self.html.span("Admin Notes:", "font-semibold"),
                self.html.span(obj.admin_notes, "")
            ], separator=" "))

        if obj.transaction_hash:
            details.append(self.html.inline([
                self.html.span("Transaction Hash:", "font-semibold"),
                self.html.span(f"<code>{obj.transaction_hash}</code>", "")
            ], separator=" "))

        if obj.crypto_amount:
            details.append(self.html.inline([
                self.html.span("Crypto Amount:", "font-semibold"),
                self.html.span(f"{obj.crypto_amount:.8f} {obj.currency.token}", "")
            ], separator=" "))

        if obj.approved_at:
            details.append(self.html.inline([
                self.html.span("Approved At:", "font-semibold"),
                self.html.span(str(obj.approved_at), "")
            ], separator=" "))

        if obj.completed_at:
            details.append(self.html.inline([
                self.html.span("Completed At:", "font-semibold"),
                self.html.span(str(obj.completed_at), "")
            ], separator=" "))

        if obj.rejected_at:
            details.append(self.html.inline([
                self.html.span("Rejected At:", "font-semibold"),
                self.html.span(str(obj.rejected_at), "")
            ], separator=" "))

        return "<br>".join(details)

    withdrawal_details_display.short_description = "Withdrawal Details"
