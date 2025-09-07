"""
User admin configuration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from ..models import CustomUser
from .filters import UserStatusFilter
from .inlines import UserRegistrationSourceInline, UserActivityInline


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = [
        "avatar",
        "email",
        "full_name",
        "status",
        "sources_count",
        "activity_count",
        "last_login_display",
        "date_joined_display",
    ]
    list_display_links = ["avatar", "email", "full_name"]
    search_fields = ["email", "first_name", "last_name"]
    list_filter = [UserStatusFilter, "is_staff", "is_active", "date_joined"]
    ordering = ["-date_joined"]
    readonly_fields = ["date_joined", "last_login"]
    inlines = [UserRegistrationSourceInline, UserActivityInline]

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": ("email", "first_name", "last_name", "avatar"),
            },
        ),
        (
            "Contact Information",
            {
                "fields": ("company", "phone", "position"),
            },
        ),
        (
            "Authentication",
            {
                "fields": ("password",),
                "classes": ("collapse",),
            },
        ),
        (
            "Permissions & Status",
            {
                "fields": (
                    ("is_active", "is_staff", "is_superuser"),
                    ("groups",),
                    ("user_permissions",),
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    def full_name(self, obj):
        """Get user's full name."""
        return obj.__class__.objects.get_full_name(obj) or "—"

    full_name.short_description = "Full Name"

    def status(self, obj):
        """Enhanced status display with icons."""
        if obj.is_superuser:
            return format_html('<span style="color: #dc3545;">👑 Superuser</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #fd7e14;">⚙️ Staff</span>')
        elif obj.is_active:
            return format_html('<span style="color: #198754;">✅ Active</span>')
        else:
            return format_html('<span style="color: #6c757d;">❌ Inactive</span>')

    status.short_description = "Status"

    def sources_count(self, obj):
        """Show count of sources for user."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return "—"
        return f"{count} source{'s' if count != 1 else ''}"

    sources_count.short_description = "Sources"

    def activity_count(self, obj):
        """Show count of user activities."""
        count = obj.activities.count()
        if count == 0:
            return "—"
        return f"{count} activit{'ies' if count != 1 else 'y'}"

    activity_count.short_description = "Activities"

    def last_login_display(self, obj):
        """Last login with natural time."""
        if obj.last_login:
            return naturaltime(obj.last_login)
        return "Never"

    last_login_display.short_description = "Last Login"

    def date_joined_display(self, obj):
        """Join date with natural day."""
        return naturalday(obj.date_joined)

    date_joined_display.short_description = "Joined"

    def avatar(self, obj):
        """Enhanced avatar display."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url,
            )
        else:
            initials = obj.__class__.objects.get_initials(obj)
            return format_html(
                '<div style="width: 32px; height: 32px; border-radius: 50%; background: #6c757d; '
                "color: white; display: flex; align-items: center; justify-content: center; "
                'font-weight: bold; font-size: 12px;">{}</div>',
                initials,
            )

    avatar.short_description = "Avatar"
