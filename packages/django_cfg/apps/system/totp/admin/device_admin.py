"""Admin interface for TOTP Device model."""

from django.contrib import admin

from django_cfg.modules.django_admin import computed_field, Icons
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import DeviceStatus, TOTPDevice
from .config import totpdevice_config


def disable_devices(modeladmin, request, queryset):
    """Disable multiple devices."""
    count = queryset.update(status=DeviceStatus.DISABLED, is_primary=False)
    from django.contrib import messages
    messages.success(request, f"Disabled {count} device(s)")


def enable_devices(modeladmin, request, queryset):
    """Enable multiple devices."""
    count = queryset.filter(status=DeviceStatus.DISABLED).update(
        status=DeviceStatus.ACTIVE
    )
    from django.contrib import messages
    messages.success(request, f"Enabled {count} device(s)")


@admin.register(TOTPDevice)
class TOTPDeviceAdmin(PydanticAdmin):
    """
    Admin interface for TOTP devices.

    Features:
    - Status badges with color coding
    - Secret masking for security
    - Device management actions
    - Usage statistics tracking
    """

    config = totpdevice_config

    @computed_field("User", ordering="user__email")
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email

    @computed_field("Status", ordering="status")
    def status_badge(self, obj):
        """Display status as colored badge."""
        variant_map = {
            DeviceStatus.PENDING: "warning",
            DeviceStatus.ACTIVE: "success",
            DeviceStatus.DISABLED: "danger",
        }
        icon_map = {
            DeviceStatus.PENDING: Icons.SCHEDULE,
            DeviceStatus.ACTIVE: Icons.CHECK_CIRCLE,
            DeviceStatus.DISABLED: Icons.CANCEL,
        }
        
        return self.html.badge(
            obj.get_status_display(),
            variant=variant_map.get(obj.status, "secondary"),
            icon=icon_map.get(obj.status, Icons.INFO)
        )

    @computed_field("Secret")
    def secret_display(self, obj):
        """Hide secret for security, show only hint."""
        if obj.secret:
            return self.html.span(f"***{obj.secret[-4:]}", "font-mono text-gray-500")
        return self.html.empty()
