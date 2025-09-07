"""
Inline admin classes for Accounts app.
"""

from unfold.admin import TabularInline
from ..models import UserRegistrationSource, UserActivity


class UserRegistrationSourceInline(TabularInline):
    model = UserRegistrationSource
    extra = 0
    readonly_fields = ["registration_date"]
    fields = ["source", "first_registration", "registration_date"]

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class RegistrationSourceInline(TabularInline):
    model = UserRegistrationSource
    extra = 0
    readonly_fields = ["registration_date"]
    fields = ["user", "first_registration", "registration_date"]

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class UserActivityInline(TabularInline):
    model = UserActivity
    extra = 0
    readonly_fields = ["created_at"]
    fields = ["activity_type", "description", "ip_address", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
