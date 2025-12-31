"""
gRPC API Key Admin.

PydanticAdmin for GrpcApiKey model with enhanced UI and status tracking.

Security:
    - API keys are stored as SHA-256 hashes
    - Full key is shown only ONCE during creation
    - Only prefix (first 8 chars) is displayed after creation
"""

from django.contrib import admin, messages
from django.utils.html import format_html
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
    - Secure key storage (SHA-256 hash)
    - Key shown only once during creation
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

    @computed_field("Key Prefix")
    def key_prefix_display(self, obj):
        """Display key prefix (first 8 chars) for identification."""
        prefix = obj.display_prefix
        return self.html.code(f"{prefix}...")

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

    # Override save to use secure generation
    def save_model(self, request, obj, form, change):
        """
        Save model with secure key generation.

        For new keys, uses GrpcApiKey.generate() and shows the key once.
        """
        if not change:  # New object
            # Use secure generation
            api_key, raw_key = GrpcApiKey.generate(
                user=obj.user,
                name=obj.name,
                description=obj.description or "",
                expires_at=obj.expires_at,
            )

            # Copy the ID to obj so Django admin works correctly
            obj.pk = api_key.pk
            obj.id = api_key.id

            # Show the key to the user (ONLY ONCE!)
            self.message_user(
                request,
                format_html(
                    '🔑 <strong>API Key Created!</strong> '
                    '<span style="background:#1a1a1a; color:#00ff00; padding:4px 8px; '
                    'font-family:monospace; border-radius:4px; user-select:all;">{}</span> '
                    '<br><strong>⚠️ Save this key now! It will NOT be shown again.</strong>',
                    raw_key
                ),
                messages.WARNING,
            )
        else:
            # Existing object - just save normally
            super().save_model(request, obj, form, change)

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

    @admin.action(description="Regenerate selected API keys")
    def regenerate_selected_keys(self, request, queryset):
        """
        Regenerate selected API keys.

        Creates new keys with the same settings but new key values.
        Old keys are revoked.
        """
        regenerated = 0
        for old_key in queryset:
            # Create new key with same settings
            new_key, raw_key = GrpcApiKey.generate(
                user=old_key.user,
                name=f"{old_key.name} (regenerated)",
                description=old_key.description,
                expires_at=old_key.expires_at,
            )

            # Revoke old key
            old_key.is_active = False
            old_key.save(update_fields=["is_active"])

            regenerated += 1

            # Show the new key
            self.message_user(
                request,
                format_html(
                    '🔑 <strong>Regenerated:</strong> {} → '
                    '<span style="background:#1a1a1a; color:#00ff00; padding:4px 8px; '
                    'font-family:monospace; border-radius:4px;">{}</span>',
                    old_key.name,
                    raw_key
                ),
                messages.WARNING,
            )

        self.message_user(
            request,
            f"⚠️ Save the keys above! They will NOT be shown again. "
            f"Regenerated {regenerated} key(s), old keys revoked.",
            messages.WARNING,
        )

    actions = ["revoke_selected_keys", "regenerate_selected_keys"]


__all__ = ["GrpcApiKeyAdmin"]
