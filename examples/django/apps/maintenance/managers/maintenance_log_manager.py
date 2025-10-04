"""
MaintenanceLog custom manager.

Simplified manager with useful query methods for logs.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta


class MaintenanceLogQuerySet(models.QuerySet):
    """Custom queryset for MaintenanceLog with useful filters."""
    
    def successful(self):
        """Get successful operations."""
        return self.filter(status='success')
    
    def failed(self):
        """Get failed operations."""
        return self.filter(status='failed')
    
    def pending(self):
        """Get pending operations."""
        return self.filter(status='pending')
    
    def by_action(self, action: str):
        """Filter by action type."""
        return self.filter(action=action)
    
    def enable_actions(self):
        """Get enable maintenance actions."""
        return self.filter(action='enable')
    
    def disable_actions(self):
        """Get disable maintenance actions."""
        return self.filter(action='disable')
    
    def sync_actions(self):
        """Get sync actions."""
        return self.filter(action='sync')
    
    def error_actions(self):
        """Get error actions."""
        return self.filter(action='error')
    
    def for_site(self, site):
        """Get logs for specific site."""
        return self.filter(site=site)
    
    def for_domain(self, domain: str):
        """Get logs for specific domain."""
        return self.filter(site__domain=domain)
    
    def recent(self, days: int = 7):
        """Get recent logs."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def today(self):
        """Get today's logs."""
        today = timezone.now().date()
        return self.filter(created_at__date=today)
    
    def with_errors(self):
        """Get logs that have error messages."""
        return self.filter(error_message__isnull=False).exclude(error_message='')
    
    def with_cloudflare_response(self):
        """Get logs that have Cloudflare response data."""
        return self.filter(cloudflare_response__isnull=False)
    
    def fast_operations(self, max_seconds: int = 5):
        """Get operations that completed quickly."""
        return self.filter(duration_seconds__lte=max_seconds)
    
    def slow_operations(self, min_seconds: int = 30):
        """Get operations that took a long time."""
        return self.filter(duration_seconds__gte=min_seconds)
    
    def search(self, query: str):
        """Search logs by reason or error message."""
        return self.filter(
            models.Q(reason__icontains=query) |
            models.Q(error_message__icontains=query) |
            models.Q(site__name__icontains=query) |
            models.Q(site__domain__icontains=query)
        )


class MaintenanceLogManager(models.Manager):
    """Custom manager for MaintenanceLog."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return MaintenanceLogQuerySet(self.model, using=self._db)
    
    def successful(self):
        """Get successful operations."""
        return self.get_queryset().successful()
    
    def failed(self):
        """Get failed operations."""
        return self.get_queryset().failed()
    
    def pending(self):
        """Get pending operations."""
        return self.get_queryset().pending()
    
    def recent(self, days: int = 7):
        """Get recent logs."""
        return self.get_queryset().recent(days)
    
    def today(self):
        """Get today's logs."""
        return self.get_queryset().today()
    
    def for_site(self, site):
        """Get logs for site."""
        return self.get_queryset().for_site(site)
    
    def for_domain(self, domain: str):
        """Get logs for domain."""
        return self.get_queryset().for_domain(domain)
    
    def with_errors(self):
        """Get logs with errors."""
        return self.get_queryset().with_errors()
    
    def search(self, query: str):
        """Search logs."""
        return self.get_queryset().search(query)
    
    def get_stats(self):
        """Get log statistics."""
        total = self.count()
        successful = self.successful().count()
        failed = self.failed().count()
        pending = self.pending().count()
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'pending': pending,
            'success_rate': (successful / total * 100) if total > 0 else 0,
        }
    
    def get_recent_activity(self, days: int = 7, limit: int = 10):
        """Get recent activity summary."""
        return self.recent(days).order_by('-created_at')[:limit]
