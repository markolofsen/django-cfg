"""
Scheduled maintenance model.

Allows planning and automatic execution of maintenance windows.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class ScheduledMaintenance(models.Model):
    """Scheduled maintenance events for sites."""
    
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"
    
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Maintenance event title")
    description = models.TextField(blank=True, help_text="Detailed description of maintenance")
    
    # Scheduling
    scheduled_start = models.DateTimeField(help_text="When maintenance should start")
    estimated_duration = models.DurationField(help_text="Expected duration of maintenance")
    scheduled_end = models.DateTimeField(editable=False, help_text="Auto-calculated end time")
    
    # Target Sites
    sites = models.ManyToManyField(
        'CloudflareSite', 
        related_name='scheduled_maintenances',
        help_text="Sites affected by this maintenance"
    )
    
    # Execution Details
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.SCHEDULED
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Configuration
    maintenance_message = models.TextField(
        blank=True,
        help_text="Custom message to display during maintenance"
    )
    template = models.CharField(
        max_length=50,
        default="modern",
        choices=[
            ("modern", "Modern"),
            ("simple", "Simple"),
            ("premium", "Premium"),
            ("minimal", "Minimal"),
        ],
        help_text="Maintenance page template"
    )
    
    # Automation Settings
    auto_enable = models.BooleanField(
        default=True, 
        help_text="Automatically enable maintenance at scheduled time"
    )
    auto_disable = models.BooleanField(
        default=True, 
        help_text="Automatically disable maintenance after duration"
    )
    
    # Notifications
    notify_before = models.DurationField(
        default=timedelta(hours=1),
        help_text="Send notification before maintenance starts"
    )
    notify_on_start = models.BooleanField(default=True)
    notify_on_complete = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, help_text="Who created this maintenance")
    
    # Execution Results
    execution_log = models.JSONField(
        default=dict,
        blank=True,
        help_text="Log of execution steps and results"
    )
    
    class Meta:
        ordering = ['scheduled_start']
        verbose_name = "Scheduled Maintenance"
        verbose_name_plural = "Scheduled Maintenances"
        indexes = [
            models.Index(fields=['status', 'scheduled_start']),
            models.Index(fields=['scheduled_start']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-calculate scheduled_end."""
        if self.scheduled_start and self.estimated_duration:
            self.scheduled_end = self.scheduled_start + self.estimated_duration
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate the scheduled maintenance."""
        if self.scheduled_start and self.scheduled_start <= timezone.now():
            if self.status == self.Status.SCHEDULED:
                raise ValidationError("Scheduled start time must be in the future")
        
        if self.estimated_duration and self.estimated_duration <= timedelta(0):
            raise ValidationError("Estimated duration must be positive")
    
    def __str__(self):
        status_emoji = {
            self.Status.SCHEDULED: "📅",
            self.Status.ACTIVE: "🔧",
            self.Status.COMPLETED: "✅",
            self.Status.CANCELLED: "❌",
            self.Status.FAILED: "💥"
        }.get(self.status, "❓")
        
        return f"{status_emoji} {self.title} - {self.scheduled_start.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def affected_sites_count(self) -> int:
        """Count total affected sites."""
        return self.sites.count()
    
    @property
    def is_due(self) -> bool:
        """Check if maintenance is due to start."""
        return (
            self.status == self.Status.SCHEDULED and
            timezone.now() >= self.scheduled_start
        )
    
    @property
    def is_overdue(self) -> bool:
        """Check if maintenance should have ended."""
        return (
            self.status == self.Status.ACTIVE and
            timezone.now() >= self.scheduled_end
        )
    
    @property
    def time_until_start(self) -> Optional[timedelta]:
        """Time until maintenance starts."""
        if self.status == self.Status.SCHEDULED:
            return self.scheduled_start - timezone.now()
        return None
    
    @property
    def time_until_end(self) -> Optional[timedelta]:
        """Time until maintenance ends."""
        if self.status == self.Status.ACTIVE:
            return self.scheduled_end - timezone.now()
        return None
    
    @property
    def actual_duration(self) -> Optional[timedelta]:
        """Actual duration of maintenance."""
        if self.actual_start and self.actual_end:
            return self.actual_end - self.actual_start
        return None
    
    def start_maintenance(self) -> Dict[str, Any]:
        """Start the scheduled maintenance."""
        if self.status != self.Status.SCHEDULED:
            return {
                'success': False,
                'error': f'Cannot start maintenance in {self.status} status'
            }
        
        from ..services.bulk_operations_service import bulk_operations
        
        # Update status
        self.status = self.Status.ACTIVE
        self.actual_start = timezone.now()
        self.save()
        
        # Enable maintenance for all sites
        sites_queryset = bulk_operations.sites(self.sites.all())
        result = sites_queryset.enable_maintenance(
            reason=self.maintenance_message or f"Scheduled maintenance: {self.title}",
            template=self.template
        )
        
        # Log execution
        self.execution_log['start'] = {
            'timestamp': timezone.now().isoformat(),
            'result': result,
            'sites_affected': result['total']
        }
        self.save()
        
        return {
            'success': True,
            'sites_affected': result['total'],
            'successful': len(result['successful']),
            'failed': len(result['failed'])
        }
    
    def complete_maintenance(self) -> Dict[str, Any]:
        """Complete the scheduled maintenance."""
        if self.status != self.Status.ACTIVE:
            return {
                'success': False,
                'error': f'Cannot complete maintenance in {self.status} status'
            }
        
        from ..services.bulk_operations_service import bulk_operations
        
        # Disable maintenance for all sites
        sites_queryset = bulk_operations.sites(self.sites.all())
        result = sites_queryset.disable_maintenance()
        
        # Update status
        self.status = self.Status.COMPLETED
        self.actual_end = timezone.now()
        
        # Log execution
        self.execution_log['complete'] = {
            'timestamp': timezone.now().isoformat(),
            'result': result,
            'sites_affected': result['total']
        }
        self.save()
        
        return {
            'success': True,
            'sites_affected': result['total'],
            'successful': len(result['successful']),
            'failed': len(result['failed']),
            'actual_duration': self.actual_duration.total_seconds() if self.actual_duration else None
        }
    
    def cancel_maintenance(self, reason: str = "") -> Dict[str, Any]:
        """Cancel the scheduled maintenance."""
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return {
                'success': False,
                'error': f'Cannot cancel maintenance in {self.status} status'
            }
        
        # If active, disable maintenance first
        if self.status == self.Status.ACTIVE:
            self.complete_maintenance()
        
        # Update status
        self.status = self.Status.CANCELLED
        
        # Log cancellation
        self.execution_log['cancelled'] = {
            'timestamp': timezone.now().isoformat(),
            'reason': reason
        }
        self.save()
        
        return {
            'success': True,
            'reason': reason
        }
    
    @classmethod
    def get_due_maintenances(cls):
        """Get maintenances that are due to start."""
        return cls.objects.filter(
            status=cls.Status.SCHEDULED,
            scheduled_start__lte=timezone.now()
        )
    
    @classmethod
    def get_overdue_maintenances(cls):
        """Get active maintenances that should have ended."""
        return cls.objects.filter(
            status=cls.Status.ACTIVE,
            scheduled_end__lte=timezone.now()
        )
    
    @classmethod
    def get_upcoming_maintenances(cls, hours: int = 24):
        """Get maintenances starting within specified hours."""
        return cls.objects.filter(
            status=cls.Status.SCHEDULED,
            scheduled_start__lte=timezone.now() + timedelta(hours=hours),
            scheduled_start__gte=timezone.now()
        )
