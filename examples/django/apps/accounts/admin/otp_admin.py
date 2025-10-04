"""
OTP admin interface using Django Admin Utilities.

Enhanced OTP management with status indicators and time displays.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    DateTimeDisplayConfig,
    StatusBadgeConfig,
    Icons,
    display
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import OTPSecret
from .filters import OTPStatusFilter


@admin.register(OTPSecret)
class OTPSecretAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Enhanced OTP admin using Django Admin Utilities."""
    
    list_display = [
        'email_display',
        'secret_display',
        'status_display',
        'created_display',
        'expires_display'
    ]
    list_display_links = ['email_display', 'secret_display']
    list_filter = [OTPStatusFilter, 'is_used', 'created_at']
    search_fields = ['email', 'secret']
    readonly_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']

    fieldsets = (
        (
            "OTP Details",
            {
                "fields": ("email", "secret", "is_used"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "expires_at"),
                "classes": ("collapse",),
            },
        ),
    )
    
    @display(description="Email")
    def email_display(self, obj):
        """Email display with email icon."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EMAIL)
        return StatusBadge.create(
            text=obj.email,
            variant="info",
            config=config
        )
    
    @display(description="Secret")
    def secret_display(self, obj):
        """Secret display with key icon."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.KEY)
        return StatusBadge.create(
            text=obj.secret,
            variant="secondary",
            config=config
        )
    
    @display(description="Status", label=True)
    def status_display(self, obj):
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
        
        config = StatusBadgeConfig(
            show_icons=True,
            icon=icon,
            custom_mappings={status: variant}
        )
        
        return self.display_status_auto(
            type('obj', (), {'status': status})(),
            'status',
            config
        )
    
    @display(description="Created")
    def created_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Expires")
    def expires_display(self, obj):
        """Expires time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'expires_at', config)
