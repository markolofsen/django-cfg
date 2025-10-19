"""
Currency Admin v2.0 - NEW Declarative Pydantic Approach (TEST)

Testing new django_admin module with real Currency model.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    BooleanField,
    TextField,
    DateTimeField,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Currency
from .actions import activate_currencies, deactivate_currencies

# ✅ Declarative Pydantic Config
currency_config = AdminConfig(
    model=Currency,

    list_display=[
        "code",
        "name",
        "token",
        "network",
        "is_active",
        "sort_order",
        "updated_at"
    ],

    display_fields=[
        BadgeField(
            name="code",
            title="Code",
            variant="primary",
            icon=Icons.CURRENCY_BITCOIN
        ),
        TextField(
            name="name",
            title="Name"
        ),
        BadgeField(
            name="token",
            title="Token",
            variant="info",
            icon=Icons.ATTACH_MONEY
        ),
        BadgeField(
            name="network",
            title="Network",
            variant="warning",
            icon=Icons.CLOUD,
            empty_value="N/A"
        ),
        BooleanField(
            name="is_active",
            title="Status"
        ),
        TextField(
            name="sort_order",
            title="Sort Order"
        ),
        DateTimeField(
            name="updated_at",
            title="Updated",
            ordering="updated_at"
        ),
    ],

    list_filter=[
        "is_active",
        "token",
        "network",
        "updated_at"
    ],

    search_fields=["code", "name", "token", "network"],
    readonly_fields=["created_at", "updated_at"],

    fieldsets=[
        FieldsetConfig(
            title="Currency Information",
            fields=["code", "name", "token", "network", "symbol"]
        ),
        FieldsetConfig(
            title="Provider Settings",
            fields=["provider", "min_amount_usd", "decimal_places"]
        ),
        FieldsetConfig(
            title="Display Settings",
            fields=["is_active", "sort_order"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],

    actions=[
        ActionConfig(
            name="activate_currencies",
            description="Activate currencies",
            variant="success",
            handler=activate_currencies
        ),
        ActionConfig(
            name="deactivate_currencies",
            description="Deactivate currencies",
            variant="warning",
            handler=deactivate_currencies
        )
    ],

    ordering=["code"],
    list_per_page=100
)

# ✅ Minimal Admin Class
@admin.register(Currency)
class CurrencyAdmin(PydanticAdmin):
    """Currency admin using NEW Pydantic declarative approach."""
    config = currency_config
