"""Admin interface for Backup Code model."""

from django.contrib import admin

from django_cfg.modules.django_admin import computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import BackupCode
from .config import backupcode_config


@admin.register(BackupCode)
class BackupCodeAdmin(PydanticAdmin):
    """
    Admin interface for backup codes.

    Features:
    - Read-only display
    - Hash masking for security
    - Usage tracking
    - No manual editing allowed
    """

    config = backupcode_config

    def has_add_permission(self, request):
        """Disable manual adding of backup codes."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of backup codes."""
        return False

    @computed_field("User", ordering="user__email")
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email

    @computed_field("Code Hash")
    def code_hash_display(self, obj):
        """Show only hash hint for security."""
        if obj.code_hash:
            return self.html.span(f"***{obj.code_hash[-8:]}", "font-mono text-gray-500")
        return self.html.empty()
