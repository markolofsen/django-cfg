"""
OTP admin configuration.
"""

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin

from ..models import OTPSecret
from .filters import OTPStatusFilter


@admin.register(OTPSecret)
class OTPSecretAdmin(ModelAdmin):
    list_display = ["email", "secret", "status", "created", "expires"]
    list_display_links = ["email", "secret"]
    list_filter = [OTPStatusFilter, "is_used", "created_at"]
    search_fields = ["email", "secret"]
    readonly_fields = ["created_at", "expires_at"]
    ordering = ["-created_at"]

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

    def status(self, obj):
        """Simple OTP status."""
        if obj.is_used:
            return "Used"
        elif obj.is_valid:
            return "✅ Valid"
        else:
            return "⏰ Expired"

    status.short_description = "Status"

    def created(self, obj):
        """Created time with natural time."""
        return naturaltime(obj.created_at)

    created.short_description = "Created"

    def expires(self, obj):
        """Expires time with natural time."""
        return naturaltime(obj.expires_at)

    expires.short_description = "Expires"
