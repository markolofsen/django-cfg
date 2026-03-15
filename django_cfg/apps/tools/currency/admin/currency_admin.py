"""
Currency Admin Configuration

Admin interface for Currency metadata model using django_cfg.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    DocumentationConfig,
    FieldsetConfig,
    TextField,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from django_cfg.apps.tools.currency.models import Currency


# ========== ADMIN CONFIG ==========
currency_admin_config = AdminConfig(
    model=Currency,

    # ========== LIST VIEW ==========
    list_display=[
        "code",
        "name",
        "symbol",
        "currency_type",
        "decimals",
        "is_active",
    ],

    # ========== DISPLAY FIELDS ==========
    display_fields=[
        TextField(
            name="code",
            title="Code",
        ),
        TextField(
            name="name",
            title="Name",
        ),
        TextField(
            name="symbol",
            title="Symbol",
        ),
        BadgeField(
            name="currency_type",
            title="Type",
            label_map={
                "fiat": "info",
                "crypto": "warning",
            },
            icon=Icons.MONETIZATION_ON,
        ),
        BadgeField(
            name="is_active",
            title="Active",
            label_map={
                True: "success",
                False: "secondary",
            },
            icon=Icons.CHECK_CIRCLE,
        ),
        DateTimeField(
            name="updated_at",
            title="Updated",
            show_relative=True,
        ),
    ],

    # ========== LIST OPTIONS ==========
    list_filter=["currency_type", "is_active"],
    search_fields=["code", "name"],
    ordering=["code"],

    # ========== FIELDSETS ==========
    fieldsets=[
        FieldsetConfig(
            title="Currency Info",
            fields=["code", "name", "symbol"],
        ),
        FieldsetConfig(
            title="Settings",
            fields=["currency_type", "decimals", "is_active"],
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True,
        ),
    ],

    # ========== FORM OPTIONS ==========
    readonly_fields=["created_at", "updated_at"],

    # ========== DOCUMENTATION ==========
    documentation=DocumentationConfig(
        source_dir="apps/tools/currency/@docs",
        title="Currency Documentation",
        show_management_commands=False,
        enable_plugins=True,
    ),
)


@admin.register(Currency)
class CurrencyAdmin(PydanticAdmin):
    """Admin for Currency metadata model."""

    config = currency_admin_config
