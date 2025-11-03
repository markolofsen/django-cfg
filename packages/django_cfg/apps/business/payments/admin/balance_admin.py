"""
Balance Admin v2.0 - NEW Declarative Pydantic Approach

Clean, modern balance and transaction management using Unfold Admin with declarative config.
"""

from django.contrib import admin
from django.db.models import Count

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    CurrencyField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    UserField,
    annotated_field,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Transaction, UserBalance
from .balance_actions import reset_zero_balances
from .filters import BalanceRangeFilter, RecentActivityFilter, TransactionTypeFilter


# ===== UserBalance Admin =====

userbalance_config = AdminConfig(
    model=UserBalance,

    # Performance optimization
    select_related=["user"],
    annotations={
        'transaction_count': Count('user__payment_transactions_v2')
    },

    # List display
    list_display=[
        "user",
        "balance_usd",
        "status",
        "total_deposited",
        "total_withdrawn",
        "transaction_count",
        "updated_at"
    ],

    # Display fields with NEW specialized classes
    display_fields=[
        UserField(
            name="user",
            title="User",
            header=True
        ),
        CurrencyField(
            name="balance_usd",
            title="Balance",
            currency="USD",
            precision=2,
            ordering="balance_usd"
        ),
        CurrencyField(
            name="total_deposited",
            title="Total Deposited",
            currency="USD",
            precision=2
        ),
        CurrencyField(
            name="total_withdrawn",
            title="Total Withdrawn",
            currency="USD",
            precision=2
        ),
        DateTimeField(
            name="updated_at",
            title="Updated",
            ordering="updated_at"
        ),
    ],

    # Filters and search
    list_filter=[
        BalanceRangeFilter,
        RecentActivityFilter,
        "created_at",
        "updated_at",
    ],

    search_fields=[
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name"
    ],

    # Readonly fields
    readonly_fields=[
        "created_at",
        "updated_at",
        "last_transaction_at",
        "balance_breakdown_display"
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="User Information",
            fields=["user"]
        ),
        FieldsetConfig(
            title="Balance Details",
            fields=[
                "balance_usd",
                "total_deposited",
                "total_withdrawn"
            ]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=[
                "last_transaction_at",
                "created_at",
                "updated_at"
            ],
            collapsed=True
        ),
        FieldsetConfig(
            title="Balance Breakdown",
            fields=["balance_breakdown_display"],
            collapsed=True
        )
    ],

    # Actions with direct function references
    actions=[
        ActionConfig(
            name="reset_zero_balances",
            description="Reset zero balances",
            variant="warning",
            handler=reset_zero_balances
        ),
    ],

    # Ordering
    ordering=["-updated_at"],
)


@admin.register(UserBalance)
class UserBalanceAdmin(PydanticAdmin):
    """
    UserBalance admin for Payments v2.0 using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Clean UI with Unfold theme
    - Custom readonly fields for detail view
    """
    config = userbalance_config

    # Custom display methods using decorators
    @computed_field("Status")
    def status(self, obj):
        """Status display based on balance."""
        if obj.balance_usd <= 0:
            return "Empty"
        elif obj.balance_usd < 10:
            return "Low Balance"
        elif obj.balance_usd < 100:
            return "Active"
        else:
            return "High Balance"

    @annotated_field("Transactions", annotation_name="transaction_count")
    def transaction_count(self, obj):
        """Transaction count display."""
        count = getattr(obj, 'transaction_count', 0)
        return f"{count} transactions"

    # Readonly field displays using self.html
    def balance_breakdown_display(self, obj):
        """Detailed balance breakdown for detail view using self.html."""
        if not obj.pk:
            return "Save to see breakdown"

        # Calculate net
        net = obj.total_deposited - obj.total_withdrawn

        # Transaction count
        txn_count = Transaction.objects.filter(user=obj.user).count()

        return self.html.breakdown(
            self.html.key_value(
                "Current Balance",
                self.html.number(obj.balance_usd, precision=2, prefix="$", suffix=" USD")
            ),
            self.html.key_value(
                "Total Deposited",
                self.html.number(obj.total_deposited, precision=2, prefix="$", suffix=" USD")
            ),
            self.html.key_value(
                "Total Withdrawn",
                self.html.number(obj.total_withdrawn, precision=2, prefix="$", suffix=" USD")
            ),
            self.html.key_value(
                "Net Deposits",
                self.html.number(net, precision=2, prefix="$", suffix=" USD")
            ),
            self.html.key_value(
                "Last Transaction",
                str(obj.last_transaction_at)
            ) if obj.last_transaction_at else None,
            self.html.key_value(
                "Total Transactions",
                str(txn_count)
            )
        )

    balance_breakdown_display.short_description = "Balance Breakdown"


# ===== Transaction Admin =====

transaction_config = AdminConfig(
    model=Transaction,

    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "id",
        "user",
        "transaction_type",
        "amount_usd",
        "balance_after",
        "created_at"
    ],

    # Display fields with NEW specialized classes
    display_fields=[
        BadgeField(
            name="id",
            title="ID",
            variant="info",
            icon=Icons.TAG
        ),
        UserField(
            name="user",
            title="User"
        ),
        BadgeField(
            name="transaction_type",
            title="Type",
            label_map={
                "deposit": "success",
                "withdrawal": "warning",
                "payment": "primary",
                "refund": "info",
                "fee": "secondary",
                "bonus": "success",
                "adjustment": "secondary"
            }
        ),
        CurrencyField(
            name="amount_usd",
            title="Amount",
            currency="USD",
            precision=2
        ),
        CurrencyField(
            name="balance_after",
            title="Balance After",
            currency="USD",
            precision=2
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Filters and search
    list_filter=[
        "transaction_type",
        TransactionTypeFilter,
        RecentActivityFilter,
        "created_at"
    ],

    search_fields=[
        "id",
        "user__username",
        "user__email",
        "description",
        "payment_id",
        "withdrawal_request_id"
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "user",
        "transaction_type",
        "amount_usd",
        "balance_after",
        "payment_id",
        "withdrawal_request_id",
        "description",
        "metadata",
        "created_at",
        "updated_at"
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Transaction Information",
            fields=[
                "id",
                "user",
                "transaction_type",
                "amount_usd",
                "balance_after",
                "description"
            ]
        ),
        FieldsetConfig(
            title="References",
            fields=[
                "payment_id",
                "withdrawal_request_id"
            ]
        ),
        FieldsetConfig(
            title="Metadata",
            fields=["metadata"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=[
                "created_at",
                "updated_at"
            ],
            collapsed=True
        )
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(Transaction)
class TransactionAdmin(PydanticAdmin):
    """
    Transaction admin for Payments v2.0 using NEW Pydantic declarative approach.

    Clean interface for transaction management.
    """
    config = transaction_config

    def has_add_permission(self, request):
        """Disable manual transaction creation (use managers instead)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable transaction deletion (immutable records)."""
        return False
