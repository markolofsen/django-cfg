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

        return self.html.breakdown(
            self.html.key_value("Withdrawal ID", str(obj.id)),
            self.html.key_value(
                "User",
                f"{obj.user.username} ({obj.user.email})"
            ),
            self.html.key_value(
                "Amount",
                self.html.number(obj.amount_usd, precision=2, prefix="$", suffix=" USD")
            ),
            self.html.key_value("Currency", obj.currency.code),
            self.html.key_value(
                "Wallet Address",
                self.html.code(obj.wallet_address)
            ),
            self.html.key_value("Status", obj.get_status_display()),
            self.html.key_value(
                "Network Fee",
                self.html.number(obj.network_fee_usd, precision=2, prefix="$", suffix=" USD")
            ) if obj.network_fee_usd else None,
            self.html.key_value(
                "Service Fee",
                self.html.number(obj.service_fee_usd, precision=2, prefix="$", suffix=" USD")
            ) if obj.service_fee_usd else None,
            self.html.key_value(
                "Total Fee",
                self.html.number(obj.total_fee_usd, precision=2, prefix="$", suffix=" USD")
            ) if obj.total_fee_usd else None,
            self.html.key_value(
                "Final Amount",
                self.html.number(obj.final_amount_usd, precision=2, prefix="$", suffix=" USD")
            ) if obj.final_amount_usd else None,
            self.html.key_value(
                "Approved By",
                obj.admin_user.username
            ) if obj.admin_user else None,
            self.html.key_value(
                "Admin Notes",
                obj.admin_notes
            ) if obj.admin_notes else None,
            self.html.key_value(
                "Transaction Hash",
                self.html.code(obj.transaction_hash)
            ) if obj.transaction_hash else None,
            self.html.key_value(
                "Crypto Amount",
                self.html.inline(
                    self.html.number(obj.crypto_amount, precision=8),
                    obj.currency.token,
                    separator=" "
                )
            ) if obj.crypto_amount else None,
            self.html.key_value(
                "Approved At",
                str(obj.approved_at)
            ) if obj.approved_at else None,
            self.html.key_value(
                "Completed At",
                str(obj.completed_at)
            ) if obj.completed_at else None,
            self.html.key_value(
                "Rejected At",
                str(obj.rejected_at)
            ) if obj.rejected_at else None
        )

    withdrawal_details_display.short_description = "Withdrawal Details"
