"""
Registration Source admin configuration.
"""

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin

from ..models import RegistrationSource, UserRegistrationSource
from .filters import RegistrationSourceStatusFilter
from .inlines import RegistrationSourceInline


@admin.register(RegistrationSource)
class RegistrationSourceAdmin(ModelAdmin):
    list_display = ["name", "url", "status", "users_count", "created"]
    list_display_links = ["name", "url"]
    list_filter = [RegistrationSourceStatusFilter, "is_active", "created_at"]
    search_fields = ["name", "url", "description"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    inlines = [RegistrationSourceInline]

    fieldsets = (
        (
            "Registration Source Information",
            {
                "fields": ("url", "name", "description", "is_active"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def status(self, obj):
        """Registration source status display."""
        if obj.is_active:
            return "✅ Active"
        else:
            return "❌ Inactive"

    status.short_description = "Status"

    def users_count(self, obj):
        """Show count of users for this source."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return "—"
        return f"{count} user{'s' if count != 1 else ''}"

    users_count.short_description = "Users"

    def created(self, obj):
        """Created time with natural time."""
        return naturaltime(obj.created_at)

    created.short_description = "Created"


@admin.register(UserRegistrationSource)
class UserRegistrationSourceAdmin(ModelAdmin):
    list_display = ["user", "source", "first_registration", "registration_date"]
    list_display_links = ["user", "source"]
    list_filter = ["first_registration", "registration_date", "source__is_active"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "source__name",
        "source__url",
    ]
    readonly_fields = ["registration_date"]
    ordering = ["-registration_date"]

    fieldsets = (
        (
            "User Registration Source Relationship",
            {
                "fields": ("user", "source", "first_registration"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("registration_date",),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "source")
