"""
Registration Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced registration source management with clean declarative config.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    UserField,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import RegistrationSource, UserRegistrationSource


# ===== RegistrationSource Admin =====

registrationsource_config = AdminConfig(
    model=RegistrationSource,

    # List display
    list_display=[
        "name",
        "description",
        "is_active",
        "users_count",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="name",
            title="Name",
            variant="primary",
            icon=Icons.SOURCE,
            ordering="name"
        ),
        BooleanField(
            name="is_active",
            title="Active"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Filters and search
    list_filter=["is_active", "created_at"],
    search_fields=["name", "description"],

    # Readonly fields
    readonly_fields=["created_at", "updated_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Source Details",
            fields=["name", "description", "is_active"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],

    # Ordering
    ordering=["name"],
)


@admin.register(RegistrationSource)
class RegistrationSourceAdmin(PydanticAdmin):
    """
    RegistrationSource admin using NEW Pydantic declarative approach.

    Features:
    - Clean declarative config
    - Automatic display methods
    - Material Icons integration
    """
    config = registrationsource_config

    # Custom display methods using decorators
    @computed_field("Description")
    def description(self, obj):
        """Description display with info icon."""
        if not obj.description:
            return None

        # Truncate long descriptions
        description = obj.description
        if len(description) > 50:
            description = f"{description[:47]}..."

        return self.html.badge(description, variant="info", icon=Icons.INFO)

    @computed_field("Users")
    def users_count(self, obj):
        """Count of users from this source."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return None

        return self.html.badge(f"{count} user{'s' if count != 1 else ''}", variant="info", icon=Icons.PEOPLE)


# ===== UserRegistrationSource Admin =====

userregistrationsource_config = AdminConfig(
    model=UserRegistrationSource,

    # Performance optimization
    select_related=["user", "source"],

    # List display
    list_display=[
        "user",
        "source",
        "registration_date"
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="user",
            title="User",
            header=True
        ),
        BadgeField(
            name="source",
            title="Source",
            variant="success",
            icon=Icons.SOURCE
        ),
        DateTimeField(
            name="registration_date",
            title="Registered",
            ordering="registration_date"
        ),
    ],

    # Filters and search
    list_filter=["source", "registration_date"],
    search_fields=[
        "user__email",
        "user__first_name",
        "user__last_name",
        "source__name"
    ],

    # Readonly fields
    readonly_fields=["registration_date"],

    # Date hierarchy
    date_hierarchy="registration_date",

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Registration Details",
            fields=["user", "source", "first_registration"]
        ),
        FieldsetConfig(
            title="Timestamp",
            fields=["registration_date"]
        ),
    ],

    # Ordering
    ordering=["-registration_date"],
)


@admin.register(UserRegistrationSource)
class UserRegistrationSourceAdmin(PydanticAdmin):
    """
    UserRegistrationSource admin using NEW Pydantic declarative approach.

    Features:
    - Clean declarative config
    - Automatic display methods
    - Optimized queries with select_related
    """
    config = userregistrationsource_config

    # Custom display method for source with dynamic variant
    @computed_field("Source")
    def source(self, obj):
        """Source display with source icon and dynamic color."""
        variant = "success" if obj.source.is_active else "secondary"

        return self.html.badge(obj.source.name, variant=variant
        )
