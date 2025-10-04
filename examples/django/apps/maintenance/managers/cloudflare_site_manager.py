"""
CloudflareSite custom manager.

Simplified manager with useful query methods for sites.
"""

from django.db import models
from django.utils import timezone
from typing import List
from datetime import timedelta


class CloudflareSiteQuerySet(models.QuerySet):
    """Custom queryset for CloudflareSite with useful filters."""
    
    def active(self):
        """Get active sites."""
        return self.filter(is_active=True)
    
    def inactive(self):
        """Get inactive sites."""
        return self.filter(is_active=False)
    
    def in_maintenance(self):
        """Get sites currently in maintenance mode."""
        return self.filter(maintenance_active=True)
    
    def not_in_maintenance(self):
        """Get sites not in maintenance mode."""
        return self.filter(maintenance_active=False)
    
    def by_domain(self, domain: str):
        """Filter by domain (exact or contains)."""
        if '.' in domain:
            return self.filter(domain__iexact=domain)
        else:
            return self.filter(domain__icontains=domain)
    
    def by_name(self, name: str):
        """Filter by site name."""
        return self.filter(name__icontains=name)
    
    def recent(self, days: int = 7):
        """Get recently created sites."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def recently_maintained(self, days: int = 7):
        """Get sites that had maintenance recently."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(last_maintenance_at__gte=cutoff)
    
    def with_logs(self):
        """Include related logs in query."""
        return self.prefetch_related('logs')
    
    def with_recent_logs(self, limit: int = 5):
        """Include recent logs in query."""
        from django.db.models import Prefetch
        return self.prefetch_related(
            Prefetch(
                'logs',
                queryset=self.model.logs.rel.related_model.objects.order_by('-created_at')[:limit],
                to_attr='recent_logs'
            )
        )
    
    def search(self, query: str):
        """Search sites by name or domain."""
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(domain__icontains=query)
        )


class CloudflareSiteManager(models.Manager):
    """Custom manager for CloudflareSite."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return CloudflareSiteQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get active sites."""
        return self.get_queryset().active()
    
    def inactive(self):
        """Get inactive sites."""
        return self.get_queryset().inactive()
    
    def in_maintenance(self):
        """Get sites in maintenance mode."""
        return self.get_queryset().in_maintenance()
    
    def not_in_maintenance(self):
        """Get sites not in maintenance mode."""
        return self.get_queryset().not_in_maintenance()
    
    def by_domain(self, domain: str):
        """Find site by domain."""
        return self.get_queryset().by_domain(domain)
    
    def search(self, query: str):
        """Search sites."""
        return self.get_queryset().search(query)
    
    def recent(self, days: int = 7):
        """Get recent sites."""
        return self.get_queryset().recent(days)
    
    def recently_maintained(self, days: int = 7):
        """Get recently maintained sites."""
        return self.get_queryset().recently_maintained(days)
    
    def get_stats(self):
        """Get site statistics."""
        total = self.count()
        active = self.active().count()
        in_maintenance = self.in_maintenance().count()
        
        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'in_maintenance': in_maintenance,
            'normal': active - in_maintenance,
        }
    
    def bulk_sync_all(self):
        """Bulk sync all sites with Cloudflare."""
        from ..services import SiteSyncService
        from ..models import CloudflareApiKey
        import logging
        
        logger = logging.getLogger(__name__)
        synced = 0
        errors = 0
        error_details = []
        
        # Get all active API keys
        api_keys = CloudflareApiKey.objects.filter(is_active=True)
        
        if not api_keys.exists():
            return {
                'synced': 0,
                'errors': 1,
                'error_details': ['No active API keys found']
            }
        
        for api_key in api_keys:
            try:
                sync_service = SiteSyncService(api_key)
                result = sync_service.sync_zones()
                # Count created + updated as synced
                sync_count = result.get('created', 0) + result.get('updated', 0)
                synced += sync_count
                logger.info(f"Synced {sync_count} sites for API key: {api_key.name}")
            except Exception as e:
                errors += 1
                error_msg = f"API key '{api_key.name}': {str(e)}"
                error_details.append(error_msg)
                logger.error(f"Sync failed for API key {api_key.name}: {e}")
        
        return {
            'synced': synced,
            'errors': errors,
            'error_details': error_details
        }
    
    def discover_all_sites(self):
        """Discover new sites from all API keys."""
        from ..services import SiteSyncService
        from ..models import CloudflareApiKey
        
        discovered = 0
        errors = 0
        
        # Get all active API keys
        api_keys = CloudflareApiKey.objects.filter(is_active=True)
        
        for api_key in api_keys:
            try:
                sync_service = SiteSyncService(api_key)
                result = sync_service.sync_zones(dry_run=False)
                discovered += result.get('created', 0)  # Count only newly created sites
            except Exception:
                errors += 1
        
        return {
            'discovered': discovered,
            'errors': errors
        }
