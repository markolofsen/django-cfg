"""
Inline admin classes for Accounts app using Django Admin Utilities.

Enhanced inline classes with better organization and conditional loading.
"""

from unfold.admin import TabularInline

from django_cfg.modules.base import BaseCfgModule

from ..models import UserActivity, UserRegistrationSource


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


class UserEmailLogInline(TabularInline):
    """Enhanced inline for viewing user's email logs."""

    def __init__(self, *args, **kwargs):
        # Check if newsletter app is available and enabled
        self.model = None
        try:
            base_module = BaseCfgModule()

            # Only import if newsletter is enabled
            if base_module.is_newsletter_enabled():
                from django_cfg.apps.business.newsletter.models import EmailLog
                self.model = EmailLog
        except (ImportError, Exception):
            # Newsletter app not available or not enabled
            pass

        # Only call super if we have a valid model
        if self.model:
            super().__init__(*args, **kwargs)

    extra = 0
    max_num = 15  # Limit to 15 most recent emails
    readonly_fields = ["newsletter", "campaign", "recipient", "subject", "status", "created_at", "sent_at"]
    fields = ["newsletter", "campaign", "subject", "status", "created_at", "sent_at"]
    ordering = ["-created_at"]
    verbose_name = "Email Log"
    verbose_name_plural = "Email History"

    # Show only recent emails to avoid performance issues
    def get_queryset(self, request):
        if not self.model:
            return self.model.objects.none()
        qs = super().get_queryset(request)
        # Don't slice here - let Django handle formset filtering first
        return qs.order_by('-created_at')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        # Only show if newsletter app is enabled and model exists
        if not self.model:
            return False
        try:
            base_module = BaseCfgModule()
            return base_module.is_newsletter_enabled()
        except Exception:
            return False


class UserSupportTicketsInline(TabularInline):
    """Enhanced inline for viewing user's support tickets."""

    def __init__(self, *args, **kwargs):
        # Check if support app is available and enabled
        self.model = None
        try:
            base_module = BaseCfgModule()

            # Only import if support is enabled
            if base_module.is_support_enabled():
                from django_cfg.apps.business.support.models import Ticket
                self.model = Ticket
        except (ImportError, Exception):
            # Support app not available or not enabled
            pass

        # Only call super if we have a valid model
        if self.model:
            super().__init__(*args, **kwargs)

    extra = 0
    max_num = 10  # Limit to 10 most recent tickets
    readonly_fields = ["uuid", "subject", "status", "created_at"]
    fields = ["uuid", "subject", "status", "created_at"]
    ordering = ["-created_at"]
    verbose_name = "Support Ticket"
    verbose_name_plural = "Support Tickets"

    # Show only recent tickets to avoid performance issues
    def get_queryset(self, request):
        if not self.model:
            return self.model.objects.none()
        qs = super().get_queryset(request)
        # Don't slice here - let Django handle formset filtering first
        return qs.order_by('-created_at')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        # Only show if support app is enabled and model exists
        if not self.model:
            return False
        try:
            base_module = BaseCfgModule()
            return base_module.is_support_enabled()
        except Exception:
            return False
