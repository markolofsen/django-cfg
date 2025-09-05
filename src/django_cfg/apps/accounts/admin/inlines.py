"""
Inline admin classes for Accounts app.
"""

from unfold.admin import TabularInline
from ..models import UserRegistrationSource, UserProfile, UserActivity


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


class UserProfileInline(TabularInline):
    model = UserProfile
    extra = 0
    readonly_fields = ["posts_count", "comments_count", "orders_count", "created_at", "updated_at"]
    fields = ["website", "github", "twitter", "linkedin", "company", "job_title"]

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


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
