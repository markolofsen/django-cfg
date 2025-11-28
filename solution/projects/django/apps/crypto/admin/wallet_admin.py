"""
Admin for Wallet model using django-cfg admin system v2.0 with Markdown documentation.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    MarkdownField,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from apps.crypto.models import Wallet

# Declarative Pydantic Config with Markdown Documentation
wallet_admin_config = AdminConfig(
    model=Wallet,

    # Performance optimization
    select_related=["user", "coin"],

    # List display
    list_display=[
        "user",
        "coin",
        "balance",
        "locked_balance",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="user",
            title="User",
            header=True
        ),
        BadgeField(
            name="coin",
            title="Coin",
            variant="primary",
            icon=Icons.CURRENCY_BITCOIN
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
        # Full documentation from file
        MarkdownField(
            name="get_full_documentation",
            title="📖 Wallet Documentation",
            source_file="apps/crypto/docs/wallet_documentation.md",
            collapsible=True,
            default_open=False,
            max_height="600px",
            header_icon="account_balance_wallet"
        ),
        # Quick help with dynamic content (from model method)
        MarkdownField(
            name="get_quick_help",
            title="⚡ Quick Help",
            collapsible=True,
            default_open=False,
            max_height="400px",
            header_icon="help"
        ),
    ],

    # Filters and search
    list_filter=["coin", "created_at"],
    search_fields=["user__username", "user__email", "coin__symbol", "address"],

    # Readonly fields
    readonly_fields=["created_at", "updated_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Owner & Coin",
            fields=["user", "coin"]
        ),
        FieldsetConfig(
            title="Balances",
            fields=["balance", "locked_balance", "address"]
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


@admin.register(Wallet)
class WalletAdmin(PydanticAdmin):
    """
    Enhanced admin for Wallet model using declarative Pydantic config.

    Documentation is configured via MarkdownField in display_fields.
    Uses both static file and dynamic method for content.
    """

    config = wallet_admin_config
