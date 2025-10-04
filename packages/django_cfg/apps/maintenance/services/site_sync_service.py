"""
Site synchronization service for automatic Cloudflare zone discovery.

Automatically discovers and syncs Cloudflare zones with Django models.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.utils import timezone
from django.db import transaction

from ..models import CloudflareApiKey, CloudflareSite, MaintenanceLog
from .maintenance_service import MaintenanceService
from ..utils.retry_utils import retry_on_failure, CloudflareRetryError

try:
    from cloudflare import Cloudflare
except ImportError:
    raise ImportError("cloudflare library is required. Install with: pip install cloudflare>=4.3.0")

logger = logging.getLogger(__name__)


class SiteSyncService:
    """
    Service for synchronizing CloudflareSite models with actual Cloudflare zones.
    
    Provides automatic discovery and sync of Cloudflare zones.
    """
    
    def __init__(self, api_key: CloudflareApiKey):
        """Initialize sync service with API key."""
        self.api_key = api_key
        self.client = Cloudflare(api_token=api_key.api_token)
        
    @retry_on_failure(max_retries=3)
    def discover_zones(self) -> List[Dict[str, Any]]:
        """
        Discover all zones in the Cloudflare account.
        
        Returns:
            List of zone data dictionaries
        """
        logger.info(f"Discovering zones for API key: {self.api_key.name}")
        
        try:
            zones = []
            for zone in self.client.zones.list():
                zone_data = {
                    'id': zone.id,
                    'name': zone.name,
                    'account_id': zone.account.id if zone.account else None,
                    'status': zone.status,
                    'paused': zone.paused,
                    'type': zone.type,
                    'development_mode': zone.development_mode,
                    'name_servers': zone.name_servers,
                    'created_on': zone.created_on,
                    'modified_on': zone.modified_on,
                }
                zones.append(zone_data)
                
            logger.info(f"Discovered {len(zones)} zones")
            return zones
            
        except Exception as e:
            logger.error(f"Failed to discover zones: {e}")
            raise CloudflareRetryError(f"Zone discovery failed: {e}")
    
    
    def sync_zones(self, 
                   force_update: bool = False,
                   dry_run: bool = False) -> Dict[str, Any]:
        """
        Sync discovered zones with Django models.
        
        Args:
            force_update: Update existing sites even if they haven't changed
            dry_run: Only show what would be changed without making changes
            
        Returns:
            Dict with sync statistics and results
        """
        logger.info(f"Starting zone sync (dry_run={dry_run}, force_update={force_update})")
        
        stats = {
            'discovered': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'sites': []
        }
        
        try:
            # Discover zones from Cloudflare
            cf_zones = self.discover_zones()
            stats['discovered'] = len(cf_zones)
            
            # Get existing sites for this API key
            existing_sites = {
                site.zone_id: site 
                for site in CloudflareSite.objects.filter(api_key=self.api_key)
            }
            
            # Process each discovered zone
            for zone_data in cf_zones:
                try:
                    result = self._sync_single_zone(
                        zone_data=zone_data,
                        existing_sites=existing_sites,
                        force_update=force_update,
                        dry_run=dry_run
                    )
                    
                    stats[result['action']] += 1
                    stats['sites'].append(result)
                    
                except Exception as e:
                    logger.error(f"Error syncing zone {zone_data['name']}: {e}")
                    stats['errors'] += 1
                    stats['sites'].append({
                        'domain': zone_data['name'],
                        'action': 'error',
                        'error': str(e)
                    })
            
            # Mark API key as used
            self.api_key.mark_used()
            
            logger.info(f"Zone sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Zone sync failed: {e}")
            stats['errors'] += 1
            return stats
    
    def _sync_single_zone(self,
                         zone_data: Dict[str, Any],
                         existing_sites: Dict[str, CloudflareSite],
                         force_update: bool,
                         dry_run: bool) -> Dict[str, Any]:
        """Sync a single zone with Django model."""
        zone_id = zone_data['id']
        domain = zone_data['name']
        
        if zone_id in existing_sites:
            # Site exists - check if update needed
            site = existing_sites[zone_id]
            
            needs_update = (
                force_update or
                site.domain != domain or
                site.account_id != zone_data.get('account_id')
            )
            
            if needs_update:
                if dry_run:
                    return {
                        'domain': domain,
                        'action': 'would_update',
                        'changes': self._get_site_changes(site, zone_data)
                    }
                else:
                    # Update existing site - preserve subdomain settings
                    site.domain = domain
                    site.account_id = zone_data.get('account_id', site.account_id)
                    
                    # Ensure subdomain fields are not reset to None during sync
                    if site.include_subdomains is None:
                        site.include_subdomains = True
                    if site.subdomain_list is None:
                        site.subdomain_list = ''
                    if site.maintenance_url is None:
                        site.maintenance_url = ''
                    
                    site.save()
                    
                    # Log the sync
                    MaintenanceLog.log_success(
                        site=site,
                        action=MaintenanceLog.Action.SYNC,
                        reason="Automatic zone sync - updated existing site"
                    )
                    
                    return {
                        'domain': domain,
                        'action': 'updated',
                        'site_id': site.id
                    }
            else:
                return {
                    'domain': domain,
                    'action': 'skipped',
                    'reason': 'No changes needed'
                }
        else:
            # New site - create it
            if dry_run:
                return {
                    'domain': domain,
                    'action': 'would_create',
                    'zone_data': zone_data
                }
            else:
                # Create new site with default subdomain settings
                site = CloudflareSite.objects.create(
                    name=self._generate_site_name(domain),
                    domain=domain,
                    zone_id=zone_id,
                    account_id=zone_data.get('account_id', ''),
                    api_key=self.api_key,
                    is_active=not zone_data.get('paused', False),
                    # Use default values from model
                    include_subdomains=True,  # Default: include all subdomains
                    subdomain_list='',       # Default: empty list
                    maintenance_url=''       # Default: empty URL
                )
                
                # Log the creation
                MaintenanceLog.log_success(
                    site=site,
                    action=MaintenanceLog.Action.SYNC,
                    reason="Automatic zone sync - created new site"
                )
                
                return {
                    'domain': domain,
                    'action': 'created',
                    'site_id': site.id
                }
    
    def _get_site_changes(self, site: CloudflareSite, zone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get changes that would be made to a site."""
        changes = {}
        
        if site.domain != zone_data['name']:
            changes['domain'] = {
                'old': site.domain,
                'new': zone_data['name']
            }
        
        if site.account_id != zone_data.get('account_id'):
            changes['account_id'] = {
                'old': site.account_id,
                'new': zone_data.get('account_id')
            }
        
        return changes
    
    def _generate_site_name(self, domain: str) -> str:
        """Generate a friendly site name from domain."""
        # Remove common prefixes and TLD for cleaner name
        name = domain.replace('www.', '').replace('api.', '').replace('app.', '')
        
        # Capitalize first letter
        if '.' in name:
            name = name.split('.')[0].capitalize()
        else:
            name = name.capitalize()
        
        return name
    
    def check_site_status(self, site: CloudflareSite) -> Dict[str, Any]:
        """
        Check current status of a site in Cloudflare.
        
        Args:
            site: CloudflareSite to check
            
        Returns:
            Dict with status information
        """
        try:
            # Get zone info
            zone = self.client.zones.get(zone_id=site.zone_id)
            
            # Check if maintenance worker is active
            maintenance_active = self._check_maintenance_worker(site)
            
            status_info = {
                'zone_status': zone.status,
                'zone_paused': zone.paused,
                'development_mode': zone.development_mode,
                'maintenance_active': maintenance_active,
                'last_checked': timezone.now().isoformat()
            }
            
            # Update site status - preserve subdomain settings
            site.maintenance_active = maintenance_active
            site.is_active = not zone.paused
            
            # Ensure subdomain fields are not reset to None during status update
            if site.include_subdomains is None:
                site.include_subdomains = True
            if site.subdomain_list is None:
                site.subdomain_list = ''
            if site.maintenance_url is None:
                site.maintenance_url = ''
                
            site.save()
            
            return status_info
            
        except Exception as e:
            logger.error(f"Failed to check status for {site.domain}: {e}")
            return {
                'error': str(e),
                'last_checked': timezone.now().isoformat()
            }
    
    @retry_on_failure(max_retries=2)
    def _check_maintenance_worker(self, site: CloudflareSite) -> bool:
        """Check if maintenance worker is active for site."""
        try:
            # List worker routes for the zone
            routes = self.client.workers.routes.list(zone_id=site.zone_id)
            
            # Check if any route matches our maintenance worker pattern
            maintenance_service = MaintenanceService(site)
            worker_name = maintenance_service.worker_name
            
            for route in routes.result:
                if hasattr(route, 'script') and route.script == worker_name:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Could not check maintenance worker for {site.domain}: {e}")
            return False
    
    def bulk_sync_all_api_keys(self) -> Dict[str, Any]:
        """
        Sync zones for all active API keys.
        
        Returns:
            Dict with overall sync results
        """
        logger.info("Starting bulk sync for all API keys")
        
        overall_stats = {
            'api_keys_processed': 0,
            'total_discovered': 0,
            'total_created': 0,
            'total_updated': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'api_key_results': []
        }
        
        active_api_keys = CloudflareApiKey.objects.filter(is_active=True)
        
        for api_key in active_api_keys:
            try:
                sync_service = SiteSyncService(api_key)
                result = sync_service.sync_zones()
                
                overall_stats['api_keys_processed'] += 1
                overall_stats['total_discovered'] += result['discovered']
                overall_stats['total_created'] += result['created']
                overall_stats['total_updated'] += result['updated']
                overall_stats['total_skipped'] += result['skipped']
                overall_stats['total_errors'] += result['errors']
                
                overall_stats['api_key_results'].append({
                    'api_key_name': api_key.name,
                    'success': True,
                    'stats': result
                })
                
            except Exception as e:
                logger.error(f"Failed to sync API key {api_key.name}: {e}")
                overall_stats['total_errors'] += 1
                overall_stats['api_key_results'].append({
                    'api_key_name': api_key.name,
                    'success': False,
                    'error': str(e)
                })
        
        logger.info(f"Bulk sync completed: {overall_stats}")
        return overall_stats


def sync_site_from_cloudflare(site: CloudflareSite) -> MaintenanceLog:
    """
    Convenience function to sync a single site from Cloudflare.
    
    Args:
        site: CloudflareSite to sync
        
    Returns:
        MaintenanceLog entry for the sync operation
    """
    try:
        sync_service = SiteSyncService(site.api_key)
        
        # Perform full zone sync to update site data from Cloudflare
        sync_result = sync_service.sync_zones(force_update=True)
        
        # Find the specific site result
        site_result = None
        for site_info in sync_result.get('sites', []):
            if site_info.get('domain') == site.domain:
                site_result = site_info
                break
        
        response_data = {
            'sync_result': sync_result,
            'site_result': site_result
        }
        
        if sync_result.get('errors', 0) == 0:
            return MaintenanceLog.log_success(
                site=site,
                action=MaintenanceLog.Action.SYNC,
                reason="Manual site sync - force update from Cloudflare",
                cloudflare_response=response_data
            )
        else:
            return MaintenanceLog.log_failure(
                site=site,
                action=MaintenanceLog.Action.SYNC,
                error_message=f"Sync completed with {sync_result['errors']} errors",
                cloudflare_response=response_data
            )
        
    except Exception as e:
        return MaintenanceLog.log_failure(
            site=site,
            action=MaintenanceLog.Action.SYNC,
            error_message=str(e)
        )
