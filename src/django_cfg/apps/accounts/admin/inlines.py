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


class UserEmailLogInline(TabularInline):
    """Inline for viewing user's email logs."""
    
    def __init__(self, *args, **kwargs):
        # Check if newsletter app is available and enabled
        self.model = None
        try:
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            
            # Only import if newsletter is enabled
            if base_module.is_newsletter_enabled():
                from django_cfg.apps.newsletter.models import EmailLog
                self.model = EmailLog
        except (ImportError, Exception):
            # Newsletter app not available or not enabled
            pass
        
        # Only call super if we have a valid model
        if self.model:
            super().__init__(*args, **kwargs)
    
    extra = 0
    readonly_fields = ["newsletter", "campaign", "recipient", "subject", "status", "created_at", "sent_at"]
    fields = ["newsletter", "campaign", "subject", "status", "created_at", "sent_at"]
    ordering = ["-created_at"]
    verbose_name = "Email Log"
    verbose_name_plural = "Email Logs"
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj=None):
        # Only show if newsletter app is enabled and model exists
        if not self.model:
            return False
        try:
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            return base_module.is_newsletter_enabled()
        except Exception:
            return False


class UserSupportTicketsInline(TabularInline):
    """Inline for viewing user's support tickets."""
    
    def __init__(self, *args, **kwargs):
        # Check if support app is available and enabled
        self.model = None
        try:
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            
            # Only import if support is enabled
            if base_module.is_support_enabled():
                from django_cfg.apps.support.models import Ticket
                self.model = Ticket
        except (ImportError, Exception):
            # Support app not available or not enabled
            pass
        
        # Only call super if we have a valid model
        if self.model:
            super().__init__(*args, **kwargs)
    
    extra = 0
    readonly_fields = ["uuid", "subject", "status", "created_at"]
    fields = ["uuid", "subject", "status", "created_at"]
    ordering = ["-created_at"]
    verbose_name = "Support Ticket"
    verbose_name_plural = "Support Tickets"
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj=None):
        # Only show if support app is enabled and model exists
        if not self.model:
            return False
        try:
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            return base_module.is_support_enabled()
        except Exception:
            return False
