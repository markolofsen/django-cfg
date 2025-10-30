"""
Admin for Coin model using django-cfg admin system v2.0 with Markdown documentation.

Example of declarative markdown documentation configuration.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DocumentationConfig,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from apps.crypto.models import Coin

# Declarative Pydantic Config with Markdown Documentation
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

    # 📚 Markdown Documentation Configuration
    # Directory mode: Automatically discovers all .md files recursively
    # Each file becomes a collapsible section
    documentation=DocumentationConfig(
        source_dir="docs",  # ← Relative to app! Scans apps/crypto/docs/**/*.md
        title="📚 Coin Documentation",
        collapsible=True,
        default_open=False,
        max_height="600px",
        show_on_changelist=True,   # Show above the list
        show_on_changeform=True,   # Show on edit/add page
        enable_plugins=True,
        sort_sections=True          # Sort sections alphabetically
    ),
)


@admin.register(Coin)
class CoinAdmin(PydanticAdmin):
    """
    Enhanced admin for Coin model using declarative Pydantic config.

    Documentation is configured via DocumentationConfig in AdminConfig.
    PydanticAdmin automatically uses unfold's template hooks to render documentation:
    - Above the list on changelist page (via list_before_template)
    - Before fieldsets on changeform page (via change_form_before_template)
    """

    config = coin_admin_config
