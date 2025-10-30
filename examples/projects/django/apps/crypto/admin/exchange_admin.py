"""
Admin for Exchange model using django-cfg admin system v2.0 with Markdown documentation.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    FieldsetConfig,
    Icons,
    MarkdownField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from apps.crypto.models import Exchange

# Declarative Pydantic Config with Markdown Documentation
exchange_admin_config = AdminConfig(
    model=Exchange,

    # List display
    list_display=[
        "name",
        "code",
        "volume_24h_usd",
        "rank",
        "is_active",
        "is_verified"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="name",
            title="Exchange",
            variant="primary",
            icon=Icons.BUSINESS
        ),
        BadgeField(
            name="code",
            title="Code",
            variant="info"
        ),
        CurrencyField(
            name="volume_24h_usd",
            title="24h Volume",
            currency="USD",
            precision=0
        ),
        BooleanField(
            name="is_active",
            title="Active"
        ),
        BooleanField(
            name="is_verified",
            title="Verified"
        ),
        # Full documentation from static file
        MarkdownField(
            name="get_documentation",
            title="📚 Exchange Documentation",
            source_file="apps/crypto/docs/exchange_documentation.md",
            collapsible=True,
            default_open=False,
            max_height="600px",
            header_icon="business"
        ),
        # Dynamic API integration guide (generated from model method)
        MarkdownField(
            name="get_api_guide",
            title="🔌 API Integration Guide",
            collapsible=True,
            default_open=False,
            max_height="500px",
            header_icon="api"
        ),
    ],

    # Filters and search
    list_filter=["is_active", "is_verified", "supports_api"],
    search_fields=["name", "code"],

    # Readonly fields
    readonly_fields=["created_at", "updated_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["name", "code", "slug", "description"]
        ),
        FieldsetConfig(
            title="Trading Data",
            fields=["volume_24h_usd", "rank", "num_markets", "num_coins"]
        ),
        FieldsetConfig(
            title="Fees",
            fields=["maker_fee_percent", "taker_fee_percent"]
        ),
        FieldsetConfig(
            title="Features & Status",
            fields=["is_active", "is_verified", "supports_api"]
        ),
        FieldsetConfig(
            title="Links",
            fields=["website", "logo_url"]
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


@admin.register(Exchange)
class ExchangeAdmin(PydanticAdmin):
    """
    Enhanced admin for Exchange model using declarative Pydantic config.

    Documentation is configured via MarkdownField in display_fields.
    Demonstrates both static file and dynamic method-based markdown content.
    """

    config = exchange_admin_config
