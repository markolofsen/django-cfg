"""
Admin configuration for geo models.

Uses django_cfg declarative admin with Unfold styling.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DecimalField,
    DocumentationConfig,
    FieldsetConfig,
    TextField,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import City, Country, State


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                              COUNTRY                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

country_config = AdminConfig(
    model=Country,

    # ========== LIST VIEW ==========
    list_display=[
        "name",
        "iso2",
        "iso3",
        "currency",
        "region",
        "is_active",
    ],

    # ========== DISPLAY FIELDS ==========
    display_fields=[
        TextField(name="name", title="Country", truncate=50),
        TextField(name="iso2", title="ISO2"),
        TextField(name="iso3", title="ISO3"),
        TextField(name="currency", title="Currency"),
        TextField(name="region", title="Region"),
        BadgeField(
            name="is_active",
            title="Active",
            label_map={True: "success", False: "danger"},
        ),
    ],

    # ========== LIST OPTIONS ==========
    list_filter=["region", "subregion", "is_active"],
    search_fields=["name", "iso2", "iso3", "native"],
    ordering=["name"],

    # ========== FORM OPTIONS ==========
    readonly_fields=["id"],

    # ========== FIELDSETS ==========
    fieldsets=[
        FieldsetConfig(
            title="Basic Info",
            fields=["name", "native", "iso2", "iso3", "numeric_code"],
        ),
        FieldsetConfig(
            title="Details",
            fields=["capital", "currency", "currency_name", "currency_symbol", "phonecode", "emoji"],
        ),
        FieldsetConfig(
            title="Geography",
            fields=["region", "subregion", "latitude", "longitude"],
        ),
        FieldsetConfig(
            title="Timezone",
            fields=["timezones", "tld"],
            collapsed=True,
        ),
        FieldsetConfig(
            title="Status",
            fields=["is_active"],
        ),
    ],

    # ========== DOCUMENTATION ==========
    documentation=DocumentationConfig(
        source_dir="apps/tools/geo/@docs",
        title="Geo Documentation",
        show_management_commands=False,
        enable_plugins=True,
    ),
)


@admin.register(Country)
class CountryAdmin(PydanticAdmin):
    """Admin for Country model."""
    config = country_config


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                               STATE                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

state_config = AdminConfig(
    model=State,

    # ========== PERFORMANCE ==========
    select_related=["country"],

    # ========== LIST VIEW ==========
    list_display=[
        "name",
        "iso2",
        "country",
        "type",
        "is_active",
    ],

    # ========== DISPLAY FIELDS ==========
    display_fields=[
        TextField(name="name", title="State", truncate=50),
        TextField(name="iso2", title="Code"),
        TextField(name="country", title="Country"),
        TextField(name="type", title="Type"),
        BadgeField(
            name="is_active",
            title="Active",
            label_map={True: "success", False: "danger"},
        ),
    ],

    # ========== LIST OPTIONS ==========
    list_filter=["country", "type", "is_active"],
    search_fields=["name", "iso2"],
    ordering=["country__name", "name"],

    # ========== FORM OPTIONS ==========
    autocomplete_fields=["country"],
    readonly_fields=["id"],

    # ========== FIELDSETS ==========
    fieldsets=[
        FieldsetConfig(
            title="Basic Info",
            fields=["name", "iso2", "type", "country"],
        ),
        FieldsetConfig(
            title="Geography",
            fields=["latitude", "longitude"],
        ),
        FieldsetConfig(
            title="Status",
            fields=["is_active"],
        ),
    ],
)


@admin.register(State)
class StateAdmin(PydanticAdmin):
    """Admin for State model."""
    config = state_config


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                                CITY                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

city_config = AdminConfig(
    model=City,

    # ========== PERFORMANCE ==========
    select_related=["country", "state"],

    # ========== LIST VIEW ==========
    list_display=[
        "name",
        "state",
        "country",
        "latitude",
        "longitude",
        "is_active",
    ],

    # ========== DISPLAY FIELDS ==========
    display_fields=[
        TextField(name="name", title="City", truncate=50),
        TextField(name="state", title="State"),
        TextField(name="country", title="Country"),
        DecimalField(name="latitude", title="Lat", decimal_places=4),
        DecimalField(name="longitude", title="Lng", decimal_places=4),
        BadgeField(
            name="is_active",
            title="Active",
            label_map={True: "success", False: "danger"},
        ),
    ],

    # ========== LIST OPTIONS ==========
    list_filter=["country", "is_active"],
    search_fields=["name"],
    ordering=["country__name", "name"],

    # ========== FORM OPTIONS ==========
    autocomplete_fields=["country", "state"],
    readonly_fields=["id"],

    # ========== FIELDSETS ==========
    fieldsets=[
        FieldsetConfig(
            title="Basic Info",
            fields=["name", "country", "state"],
        ),
        FieldsetConfig(
            title="Geography",
            fields=["latitude", "longitude"],
        ),
        FieldsetConfig(
            title="Status",
            fields=["is_active"],
        ),
    ],
)


@admin.register(City)
class CityAdmin(PydanticAdmin):
    """Admin for City model."""
    config = city_config
