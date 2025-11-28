"""
Django Admin for Trading app using django-cfg admin system v2.0.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    CurrencyField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from .models import Portfolio, Order


# ===== Portfolio Admin =====

portfolio_admin_config = AdminConfig(
    model=Portfolio,

    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "user",
        "total_balance_usd",
        "available_balance_usd",
        "total_trades",
        "win_rate",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="user",
            title="User",
            header=True
        ),
        CurrencyField(
            name="total_balance_usd",
            title="Total Balance",
            currency="USD",
            precision=2
        ),
        CurrencyField(
            name="available_balance_usd",
            title="Available",
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
    list_filter=["created_at"],
    search_fields=["user__username", "user__email"],

    # Readonly fields
    readonly_fields=["created_at", "updated_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Owner",
            fields=["user"]
        ),
        FieldsetConfig(
            title="Balances",
            fields=["total_balance_usd", "available_balance_usd", "locked_balance_usd"]
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["total_trades", "win_rate", "total_profit_loss_usd"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(Portfolio)
class PortfolioAdmin(PydanticAdmin):
    """Enhanced admin for Portfolio model using new Pydantic approach."""

    config = portfolio_admin_config


# ===== Order Admin =====

order_admin_config = AdminConfig(
    model=Order,

    # Performance optimization
    select_related=["portfolio", "portfolio__user"],

    # List display
    list_display=[
        "id",
        "portfolio",
        "symbol",
        "side",
        "order_type",
        "quantity",
        "price",
        "status",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="symbol",
            title="Symbol",
            variant="primary",
            icon=Icons.CURRENCY_BITCOIN
        ),
        BadgeField(
            name="side",
            title="Side",
            label_map={
                "buy": "success",
                "sell": "danger"
            }
        ),
        BadgeField(
            name="order_type",
            title="Type",
            variant="info"
        ),
        CurrencyField(
            name="price",
            title="Price",
            currency="USD",
            precision=2
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "open": "info",
                "filled": "success",
                "partially_filled": "primary",
                "cancelled": "secondary",
                "rejected": "danger"
            }
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Filters and search
    list_filter=["status", "side", "order_type", "created_at"],
    search_fields=["symbol", "portfolio__user__username"],

    # Readonly fields
    readonly_fields=["created_at", "updated_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Order Details",
            fields=["portfolio", "symbol", "side", "order_type"]
        ),
        FieldsetConfig(
            title="Pricing",
            fields=["quantity", "price", "stop_price", "total_value"]
        ),
        FieldsetConfig(
            title="Execution",
            fields=["status", "filled_quantity", "average_fill_price"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at", "executed_at"],
            collapsed=True
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(Order)
class OrderAdmin(PydanticAdmin):
    """Enhanced admin for Order model using new Pydantic approach."""

    config = order_admin_config
