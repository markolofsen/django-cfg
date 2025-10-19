"""
Admin for Coin model using django-cfg admin system v2.0.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from apps.crypto.models import Coin

# Declarative Pydantic Config
coin_admin_config = AdminConfig(
    model=Coin,

    # List display
    list_display=[
        "symbol",
        "name",
        "current_price_usd",
        "market_cap_usd",
        "rank",
        "is_active",
        "is_tradeable"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="symbol",
            title="Symbol",
            variant="primary",
            icon=Icons.CURRENCY_BITCOIN
        ),
        CurrencyField(
            name="current_price_usd",
            title="Price",
            currency="USD",
            precision=2
        ),
        CurrencyField(
            name="market_cap_usd",
            title="Market Cap",
            currency="USD",
            precision=0
        ),
        BooleanField(
            name="is_active",
            title="Active"
        ),
        BooleanField(
            name="is_tradeable",
            title="Tradeable"
        ),
    ],

    # Filters and search
    list_filter=["is_active", "is_tradeable", "created_at"],
    search_fields=["symbol", "name"],

    # Readonly fields
    readonly_fields=["created_at", "updated_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["symbol", "name", "slug", "description"]
        ),
        FieldsetConfig(
            title="Market Data",
            fields=["current_price_usd", "market_cap_usd", "volume_24h_usd", "rank"]
        ),
        FieldsetConfig(
            title="Status",
            fields=["is_active", "is_tradeable"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],

    # Ordering
    ordering=["rank"],

    # Auto-populate slug from name
    prepopulated_fields={'slug': ('name',)},
)


@admin.register(Coin)
class CoinAdmin(PydanticAdmin):
    """Enhanced admin for Coin model using new Pydantic approach."""

    config = coin_admin_config
