"""
MaintenanceLog model.

Simple log of all maintenance operations.
"""

from django.db import models
from .cloudflare_site import CloudflareSite


class MaintenanceLog(models.Model):
    """
    Simple log of all maintenance operations.
    
    Tracks enable/disable operations with success/failure status.
    """
    
    class Action(models.TextChoices):
        ENABLE = "enable", "Enable Maintenance"
        DISABLE = "disable", "Disable Maintenance"
        ERROR = "error", "Error"
        SYNC = "sync", "Sync from Cloudflare"
    
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        PENDING = "pending", "Pending"
    
    # Related site
    site = models.ForeignKey(
        CloudflareSite,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Site this log entry belongs to"
    )
    
    # Operation details
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        help_text="What action was performed"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        help_text="Result of the operation"
    )
    
    # Additional info
    reason = models.TextField(
        blank=True,
        help_text="Why maintenance was enabled/disabled"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error details if operation failed"
    )
    cloudflare_response = models.JSONField(
        null=True,
        blank=True,
        help_text="Full Cloudflare API response for debugging"
    )
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="How long the operation took"
    )
    
    # Custom manager
    from ..managers.maintenance_log_manager import MaintenanceLogManager
    objects = MaintenanceLogManager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Maintenance Log"
        verbose_name_plural = "Maintenance Logs"
        indexes = [
            models.Index(fields=['site', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self) -> str:
        status_emoji = {
            self.Status.SUCCESS: "✅",
            self.Status.FAILED: "❌",
            self.Status.PENDING: "⏳"
        }.get(self.status, "❓")
        
        return f"{status_emoji} {self.get_action_display()} - {self.site.domain}"
    
    @classmethod
    def log_success(cls, site: CloudflareSite, action: str, reason: str = "", 
                   duration_seconds: int = None, cloudflare_response: dict = None) -> 'MaintenanceLog':
        """Log successful operation."""
        return cls.objects.create(
            site=site,
            action=action,
            status=cls.Status.SUCCESS,
            reason=reason,
            duration_seconds=duration_seconds,
            cloudflare_response=cloudflare_response
        )
    
    @classmethod
    def log_failure(cls, site: CloudflareSite, action: str, error_message: str,
                   reason: str = "", cloudflare_response: dict = None) -> 'MaintenanceLog':
        """Log failed operation."""
        return cls.objects.create(
            site=site,
            action=action,
            status=cls.Status.FAILED,
            reason=reason,
            error_message=error_message,
            cloudflare_response=cloudflare_response
        )
    
    @classmethod
    def log_pending(cls, site: CloudflareSite, action: str, reason: str = "") -> 'MaintenanceLog':
        """Log pending operation."""
        return cls.objects.create(
            site=site,
            action=action,
            status=cls.Status.PENDING,
            reason=reason
        )


