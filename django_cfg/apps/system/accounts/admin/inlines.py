"""
Inline admin classes for Accounts app using Django Admin Utilities.

Enhanced inline classes with better organization and conditional loading.
"""

from unfold.admin import TabularInline


from ..models import UserActivity, UserAPIKey, UserRegistrationSource


class UserRegistrationSourceInline(TabularInline):
    """Enhanced inline for user registration sources."""
    model = UserRegistrationSource
    extra = 0
    readonly_fields = ["registration_date"]
    fields = ["source", "first_registration", "registration_date"]
    ordering = ["-registration_date"]
    verbose_name = "Registration Source"
    verbose_name_plural = "Registration Sources"

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class RegistrationSourceInline(TabularInline):
    """Enhanced inline for registration source users."""
    model = UserRegistrationSource
    extra = 0
    readonly_fields = ["registration_date"]
    fields = ["user", "first_registration", "registration_date"]
    ordering = ["-registration_date"]
    verbose_name = "User Registration"
    verbose_name_plural = "User Registrations"

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class UserActivityInline(TabularInline):
    """Enhanced inline for user activities."""
    model = UserActivity
    extra = 0
    max_num = 10  # Limit to 10 most recent activities
    readonly_fields = ["created_at", "activity_type", "description"]
    fields = ["activity_type", "description", "ip_address", "created_at"]
    ordering = ["-created_at"]
    verbose_name = "Activity"
    verbose_name_plural = "Recent Activities"

    # Show only recent activities to avoid performance issues
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Don't slice here - let Django handle formset filtering first
        return qs.order_by('-created_at')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


# `UserEmailLogInline` and `UserSupportTicketsInline` were REMOVED here, 2026-08-19.
#
# Both were dead from the day they were written, and in the same three ways:
#
#   1. they gated on `BaseCfgModule().is_newsletter_enabled()` /
#      `is_support_enabled()` — neither method exists (`BaseCfgModule` defines
#      eight `is_*_enabled`, neither of them these);
#   2. they imported `django_cfg.apps.business.{newsletter,support}` — there is no
#      `business` package at all (`apps/` holds api, payments, system, tools), and
#      **no `Ticket` or `Newsletter` model exists anywhere in django_cfg**;
#   3. `except (ImportError, Exception)` cannot fail, so `self.model` stayed
#      `None`, `super().__init__` was never called, and the inline resolved to
#      nothing — indistinguishable from "the feature is switched off".
#
# Their `get_queryset` also read `self.model.objects.none()` guarded by
# `if not self.model:` — i.e. `None.objects` on the exact path meant to be safe.
#
# Email history is not lost: it is a column on the user list (`emails_count`,
# repaired the same day against the real `django_cfg_mailer.EmailLog`) and a full
# page of its own at `EmailLogAdmin`. **An inline is not possible for it** —
# `EmailLog.user_id` is an `IntegerField` on purpose, because mail also goes to
# addresses with no account and a letter's record should outlive the account, and
# a `TabularInline` requires a ForeignKey to the parent.


class UserAPIKeyInline(TabularInline):
    """Inline for user's API key."""

    model = UserAPIKey
    extra = 0
    max_num = 1
    readonly_fields = ["key", "reissued_at", "created_at"]
    fields = ["key", "reissued_at", "created_at"]
    verbose_name = "API Key"
    verbose_name_plural = "API Key"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
