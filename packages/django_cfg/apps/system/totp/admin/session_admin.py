"""Admin interface for Two Factor Session model."""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from django_cfg.modules.django_admin import computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import TwoFactorSession
from .config import twofactorsession_config


def cleanup_expired_action(modeladmin, request):
    """Clean up expired sessions (changelist action)."""
    from ..services import TwoFactorSessionService
    from django.contrib import messages
    
    count = TwoFactorSessionService.cleanup_expired(older_than_hours=24)
    messages.success(request, f"Cleaned up {count} expired session(s)")
    
    return redirect(reverse('admin:django_cfg_totp_twofactorsession_changelist'))


@admin.register(TwoFactorSession)
class TwoFactorSessionAdmin(PydanticAdmin):
    """
    Admin interface for 2FA sessions.

    Features:
    - Session monitoring
    - Expired session cleanup
    - Security context display
    - Read-only interface
    """

    config = twofactorsession_config

    def has_add_permission(self, request):
        """Disable manual adding of sessions."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of sessions."""
        return False

    @computed_field("User", ordering="user__email")
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email

    @computed_field("User Agent")
    def user_agent_display(self, obj):
        """Display truncated user agent."""
        if obj.user_agent:
            ua = obj.user_agent[:100] + "..." if len(obj.user_agent) > 100 else obj.user_agent
            return self.html.span(ua, "text-xs text-gray-600")
        return self.html.empty()
