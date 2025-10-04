"""
Bulk operations service for managing multiple sites.

Provides ORM-like interface for bulk maintenance operations across multiple sites.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from django.db.models import QuerySet, Q
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models import CloudflareSite, MaintenanceLog, CloudflareApiKey
from .maintenance_service import MaintenanceService
from ..utils.retry_utils import retry_on_failure

logger = logging.getLogger(__name__)


class SiteQuerySet:
    """ORM-like interface for site operations."""
    
    def __init__(self, queryset: QuerySet[CloudflareSite]):
        self.queryset = queryset
    
    def filter(self, **kwargs) -> 'SiteQuerySet':
        """Filter sites with Django ORM syntax."""
        return SiteQuerySet(self.queryset.filter(**kwargs))
    
    def exclude(self, **kwargs) -> 'SiteQuerySet':
        """Exclude sites with Django ORM syntax."""
        return SiteQuerySet(self.queryset.exclude(**kwargs))
    
    def active(self) -> 'SiteQuerySet':
        """Filter active sites."""
        return SiteQuerySet(self.queryset.filter(is_active=True))
    
    def in_maintenance(self) -> 'SiteQuerySet':
        """Filter sites currently in maintenance."""
        return SiteQuerySet(self.queryset.filter(maintenance_active=True))
    
    def not_in_maintenance(self) -> 'SiteQuerySet':
        """Filter sites not in maintenance."""
        return SiteQuerySet(self.queryset.filter(maintenance_active=False))
    
    def by_api_key(self, api_key: Union[CloudflareApiKey, str]) -> 'SiteQuerySet':
        """Filter sites by API key."""
        if isinstance(api_key, str):
            return SiteQuerySet(self.queryset.filter(api_key__name=api_key))
        return SiteQuerySet(self.queryset.filter(api_key=api_key))
    
    def search(self, query: str) -> 'SiteQuerySet':
        """Search sites by name or domain."""
        return SiteQuerySet(
            self.queryset.filter(
                Q(name__icontains=query) | Q(domain__icontains=query)
            )
        )
    
    def count(self) -> int:
        """Count sites in queryset."""
        return self.queryset.count()
    
    def all(self) -> List[CloudflareSite]:
        """Get all sites in queryset."""
        return list(self.queryset.all())
    
    def first(self) -> Optional[CloudflareSite]:
        """Get first site in queryset."""
        return self.queryset.first()
    
    def get(self, **kwargs) -> CloudflareSite:
        """Get single site."""
        return self.queryset.get(**kwargs)
    
    # Bulk Operations
    def enable_maintenance(self, 
                          reason: str = "Bulk maintenance operation",
                          template: str = "modern",
                          max_workers: int = 5,
                          dry_run: bool = False) -> Dict[str, Any]:
        """Enable maintenance mode for all sites in queryset."""
        sites = self.queryset.filter(maintenance_active=False)
        
        if dry_run:
            return {
                'total': sites.count(),
                'would_affect': [site.domain for site in sites],
                'dry_run': True
            }
        
        return self._execute_bulk_operation(
            sites=sites,
            operation='enable',
            reason=reason,
            template=template,
            max_workers=max_workers
        )
    
    def disable_maintenance(self, 
                           max_workers: int = 5,
                           dry_run: bool = False) -> Dict[str, Any]:
        """Disable maintenance mode for all sites in queryset."""
        sites = self.queryset.filter(maintenance_active=True)
        
        if dry_run:
            return {
                'total': sites.count(),
                'would_affect': [site.domain for site in sites],
                'dry_run': True
            }
        
        return self._execute_bulk_operation(
            sites=sites,
            operation='disable',
            max_workers=max_workers
        )
    
    def check_status(self, max_workers: int = 10) -> Dict[str, Any]:
        """Check status of all sites in queryset."""
        sites = self.queryset.all()
        
        return self._execute_bulk_operation(
            sites=sites,
            operation='status',
            max_workers=max_workers
        )
    
    def sync_from_cloudflare(self, max_workers: int = 5) -> Dict[str, Any]:
        """Sync all sites from Cloudflare."""
        sites = self.queryset.all()
        
        return self._execute_bulk_operation(
            sites=sites,
            operation='sync',
            max_workers=max_workers
        )
    
    def _execute_bulk_operation(self,
                               sites: QuerySet[CloudflareSite],
                               operation: str,
                               max_workers: int = 5,
                               **kwargs) -> Dict[str, Any]:
        """Execute bulk operation on sites with threading."""
        results = {
            'total': sites.count(),
            'successful': [],
            'failed': [],
            'skipped': [],
            'operation': operation,
            'started_at': timezone.now().isoformat()
        }
        
        if results['total'] == 0:
            return results
        
        # Execute operations in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_site = {
                executor.submit(self._execute_single_operation, site, operation, **kwargs): site
                for site in sites
            }
            
            # Collect results
            for future in as_completed(future_to_site):
                site = future_to_site[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['successful'].append({
                            'domain': site.domain,
                            'result': result.get('data')
                        })
                    else:
                        results['failed'].append({
                            'domain': site.domain,
                            'error': result.get('error', 'Unknown error')
                        })
                except Exception as e:
                    logger.error(f"Bulk operation failed for {site.domain}: {e}")
                    results['failed'].append({
                        'domain': site.domain,
                        'error': str(e)
                    })
        
        results['completed_at'] = timezone.now().isoformat()
        results['success_rate'] = len(results['successful']) / results['total'] * 100
        
        logger.info(f"Bulk {operation} completed: {len(results['successful'])}/{results['total']} successful")
        return results
    
    @retry_on_failure(max_retries=2)
    def _execute_single_operation(self, 
                                 site: CloudflareSite, 
                                 operation: str, 
                                 **kwargs) -> Dict[str, Any]:
        """Execute single operation on a site."""
        try:
            service = MaintenanceService(site)
            
            if operation == 'enable':
                log_entry = service.enable_maintenance(
                    reason=kwargs.get('reason', 'Bulk operation'),
                    template=kwargs.get('template', 'modern')
                )
                return {
                    'success': log_entry.status == MaintenanceLog.Status.SUCCESS,
                    'data': {
                        'log_id': log_entry.id,
                        'duration': log_entry.duration_seconds
                    },
                    'error': log_entry.error_message if log_entry.status == MaintenanceLog.Status.FAILED else None
                }
            
            elif operation == 'disable':
                log_entry = service.disable_maintenance()
                return {
                    'success': log_entry.status == MaintenanceLog.Status.SUCCESS,
                    'data': {
                        'log_id': log_entry.id,
                        'duration': log_entry.duration_seconds
                    },
                    'error': log_entry.error_message if log_entry.status == MaintenanceLog.Status.FAILED else None
                }
            
            elif operation == 'status':
                status = service.get_status()
                return {
                    'success': True,
                    'data': {
                        'maintenance_active': status,
                        'last_checked': timezone.now().isoformat()
                    }
                }
            
            elif operation == 'sync':
                from .site_sync_service import sync_site_from_cloudflare
                log_entry = sync_site_from_cloudflare(site)
                return {
                    'success': log_entry.status == MaintenanceLog.Status.SUCCESS,
                    'data': {
                        'log_id': log_entry.id,
                        'response': log_entry.cloudflare_response
                    },
                    'error': log_entry.error_message if log_entry.status == MaintenanceLog.Status.FAILED else None
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }
                
        except Exception as e:
            logger.error(f"Operation {operation} failed for {site.domain}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class BulkOperationsService:
    """Main service for bulk operations on sites."""
    
    def __init__(self):
        """Initialize bulk operations service."""
        pass
    
    def sites(self, queryset: Optional[QuerySet[CloudflareSite]] = None) -> SiteQuerySet:
        """Get sites queryset for bulk operations."""
        if queryset is None:
            queryset = CloudflareSite.objects.all()
        
        return SiteQuerySet(queryset)
    
    def all_sites(self) -> SiteQuerySet:
        """Get all sites."""
        return self.sites()
    
    def active_sites(self) -> SiteQuerySet:
        """Get all active sites."""
        return self.sites().active()
    
    def maintenance_sites(self) -> SiteQuerySet:
        """Get sites currently in maintenance."""
        return self.sites().in_maintenance()
    
    def discover_and_create_sites(self, 
                                 api_key: CloudflareApiKey,
                                 dry_run: bool = False) -> Dict[str, Any]:
        """Discover zones from Cloudflare and create sites."""
        from .site_sync_service import SiteSyncService
        
        try:
            sync_service = SiteSyncService(api_key)
            return sync_service.sync_zones(dry_run=dry_run)
        except Exception as e:
            logger.error(f"Failed to discover sites for {api_key.name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'discovered': 0,
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'errors': 1
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics for all sites."""
        all_sites = CloudflareSite.objects.all()
        
        stats = {
            'total_sites': all_sites.count(),
            'active_sites': all_sites.filter(is_active=True).count(),
            'maintenance_sites': all_sites.filter(maintenance_active=True).count(),
            'api_keys_count': CloudflareApiKey.objects.filter(is_active=True).count(),
            'recent_logs': MaintenanceLog.objects.count(),
            'by_api_key': {}
        }
        
        # Statistics by API key
        for api_key in CloudflareApiKey.objects.filter(is_active=True):
            key_sites = all_sites.filter(api_key=api_key)
            stats['by_api_key'][api_key.name] = {
                'total': key_sites.count(),
                'active': key_sites.filter(is_active=True).count(),
                'maintenance': key_sites.filter(maintenance_active=True).count()
            }
        
        return stats
    
    def emergency_disable_all(self, 
                             reason: str = "Emergency maintenance disable",
                             max_workers: int = 10) -> Dict[str, Any]:
        """Emergency disable maintenance for all sites."""
        logger.warning("Emergency disable maintenance for ALL sites")
        
        return self.maintenance_sites().disable_maintenance(
            max_workers=max_workers
        )
    
    def emergency_enable_all(self, 
                            reason: str = "Emergency maintenance enable",
                            template: str = "minimal",
                            max_workers: int = 10) -> Dict[str, Any]:
        """Emergency enable maintenance for all sites."""
        logger.warning("Emergency enable maintenance for ALL sites")
        
        return self.active_sites().not_in_maintenance().enable_maintenance(
            reason=reason,
            template=template,
            max_workers=max_workers
        )


# Global instance
bulk_operations = BulkOperationsService()


# Convenience functions
def enable_maintenance_for_domains(domains: List[str], 
                                  reason: str = "Bulk operation",
                                  template: str = "modern") -> Dict[str, Any]:
    """Enable maintenance for specific domains."""
    sites = CloudflareSite.objects.filter(domain__in=domains)
    return bulk_operations.sites(sites).enable_maintenance(reason=reason, template=template)


def disable_maintenance_for_domains(domains: List[str]) -> Dict[str, Any]:
    """Disable maintenance for specific domains."""
    sites = CloudflareSite.objects.filter(domain__in=domains)
    return bulk_operations.sites(sites).disable_maintenance()


def bulk_sync_all_sites() -> Dict[str, Any]:
    """Sync all sites from Cloudflare."""
    return bulk_operations.all_sites().sync_from_cloudflare()


def get_maintenance_status_report() -> Dict[str, Any]:
    """Get comprehensive maintenance status report."""
    stats = bulk_operations.get_statistics()
    
    # Add recent activity
    recent_logs = MaintenanceLog.objects.order_by('-created_at')[:10]
    stats['recent_activity'] = [
        {
            'site': log.site.domain,
            'action': log.get_action_display(),
            'status': log.get_status_display(),
            'created_at': log.created_at.isoformat(),
            'duration': log.duration_seconds
        }
        for log in recent_logs
    ]
    
    return stats
