"""
OTP Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced OTP management with Material Icons and clean declarative config.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import OTPSecret
from .filters import OTPStatusFilter


# ===== OTP Admin =====

otpsecret_config = AdminConfig(
    model=OTPSecret,

    # List display
    list_display=[
        "email",
        "secret",
        "status",
        "created_at",
        "expires_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="email",
            title="Email",
            variant="info",
            icon=Icons.EMAIL
        ),
        BadgeField(
            name="secret",
            title="Secret",
            variant="secondary",
            icon=Icons.KEY
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
        DateTimeField(
            name="expires_at",
            title="Expires",
            ordering="expires_at"
        ),
    ],

    # Filters and search
    list_filter=[OTPStatusFilter, "is_used", "created_at"],
    search_fields=["email", "secret"],

    # Readonly fields
    readonly_fields=["created_at", "expires_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="OTP Details",
            fields=["email", "secret", "is_used"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "expires_at"],
            collapsed=True
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(OTPSecret)
class OTPSecretAdmin(PydanticAdmin):
    """
    OTPSecret admin using NEW Pydantic declarative approach.

    Features:
    - Clean declarative config
    - Status with dynamic icons
    - Material Icons integration
    """
    config = otpsecret_config

    # Custom display methods using decorators
    @computed_field("Status")
    def status(self, obj):
        """Enhanced OTP status with appropriate icons and colors."""
        if obj.is_used:
            status = "Used"
            icon = Icons.CHECK_CIRCLE
            variant = "secondary"
        elif obj.is_valid:
            status = "Valid"
            icon = Icons.VERIFIED
            variant = "success"
        else:
            status = "Expired"
            icon = Icons.SCHEDULE
            variant = "warning"

        return self.html.badge(status, variant=variant, icon=icon)
