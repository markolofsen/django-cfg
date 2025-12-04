"""
gRPC API Key Admin.

PydanticAdmin for GrpcApiKey model with enhanced UI and status tracking.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import GrpcApiKey
from .config import grpcapikey_config


@admin.register(GrpcApiKey)
class GrpcApiKeyAdmin(PydanticAdmin):
    """
    Admin interface for gRPC API keys.

    Features:
    - List view with status indicators
    - Search by name, description, user
    - Filter by status, type, user
    - Read-only key display (masked)
    - Actions for revoking keys
    - Type-safe configuration via AdminConfig
    """

    config = grpcapikey_config

    # Display methods
    @computed_field("Status", ordering="is_active")
    def status_indicator(self, obj):
        """Display status indicator with expiration check."""
        if obj.is_valid:
            return self.html.badge(
                "Active",
                variant="success",
                icon=Icons.CHECK_CIRCLE
            )
        elif obj.is_expired:
            return self.html.badge(
                "Expired",
                variant="warning",
                icon=Icons.SCHEDULE
            )
        else:
            return self.html.badge(
                "Revoked",
                variant="danger",
                icon=Icons.CANCEL
            )

    @computed_field("Masked Key")
    def masked_key_display(self, obj):
        """Display masked API key."""
        return self.html.code(obj.masked_key)

    def key_display(self, obj):
        """Display full API key (read-only, for copying)."""
        if obj.pk:
            return self.html.code(obj.key)
        return self.html.empty()

    key_display.short_description = "Full API Key"

    @computed_field("Requests", ordering="request_count")
    def request_count_display(self, obj):
        """Display request count with badge."""
        if obj.request_count == 0:
            return self.html.empty("0")

        # Color based on usage
        if obj.request_count > 1000:
            variant = "success"
        elif obj.request_count > 100:
            variant = "info"
        else:
            variant = "secondary"

        return self.html.badge(
            str(obj.request_count),
            variant=variant,
            icon=Icons.ANALYTICS
        )

    @computed_field("Expires", ordering="expires_at")
    def expires_display(self, obj):
        """Display expiration date with status."""
        if not obj.expires_at:
            return self.html.badge(
                "Never",
                variant="success",
                icon=Icons.ALL_INCLUSIVE
            )

        from django.utils import timezone
        if obj.expires_at < timezone.now():
            return self.html.badge(
                obj.expires_at.strftime("%Y-%m-%d"),
                variant="danger",
                icon=Icons.ERROR
            )

        return self.html.text(
            obj.expires_at.strftime("%Y-%m-%d"),
            variant="primary"
        )

    # Actions
    @admin.action(description="Revoke selected API keys")
    def revoke_selected_keys(self, request, queryset):
        """Revoke selected API keys."""
        count = queryset.filter(is_active=True).count()
        queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully revoked {count} API key(s).",
        )


__all__ = ["GrpcApiKeyAdmin"]
