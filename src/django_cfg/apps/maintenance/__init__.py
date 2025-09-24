"""
Simplified Django-CFG Maintenance Application.

A simple maintenance mode management app with Cloudflare integration.
Refactored from 119 files to ~10 files following KISS principles.

Proper structure:
- models/ - CloudflareSite and MaintenanceLog models
- services/ - MaintenanceService for Cloudflare operations
- admin/ - Simple admin interfaces
- management/commands/ - CLI commands
"""

__version__ = "2.0.0"
__author__ = "Django-CFG Team"

# Lazy import registry to avoid Django initialization issues
_LAZY_IMPORTS = {
    # Models
    'CloudflareApiKey': ('django_cfg.apps.maintenance.models', 'CloudflareApiKey'),
    'CloudflareSite': ('django_cfg.apps.maintenance.models', 'CloudflareSite'),
    'MaintenanceLog': ('django_cfg.apps.maintenance.models', 'MaintenanceLog'),
    'ScheduledMaintenance': ('django_cfg.apps.maintenance.models', 'ScheduledMaintenance'),
    
    # Services
    'MaintenanceService': ('django_cfg.apps.maintenance.services', 'MaintenanceService'),
    'SiteSyncService': ('django_cfg.apps.maintenance.services', 'SiteSyncService'),
    'BulkOperationsService': ('django_cfg.apps.maintenance.services', 'BulkOperationsService'),
    'ScheduledMaintenanceService': ('django_cfg.apps.maintenance.services', 'ScheduledMaintenanceService'),
    'bulk_operations': ('django_cfg.apps.maintenance.services', 'bulk_operations'),
    'scheduled_maintenance_service': ('django_cfg.apps.maintenance.services', 'scheduled_maintenance_service'),
    'enable_maintenance_for_domain': ('django_cfg.apps.maintenance.services', 'enable_maintenance_for_domain'),
    'disable_maintenance_for_domain': ('django_cfg.apps.maintenance.services', 'disable_maintenance_for_domain'),
    'sync_site_from_cloudflare': ('django_cfg.apps.maintenance.services', 'sync_site_from_cloudflare'),
    'enable_maintenance_for_domains': ('django_cfg.apps.maintenance.services', 'enable_maintenance_for_domains'),
    'disable_maintenance_for_domains': ('django_cfg.apps.maintenance.services', 'disable_maintenance_for_domains'),
    'bulk_sync_all_sites': ('django_cfg.apps.maintenance.services', 'bulk_sync_all_sites'),
    'get_maintenance_status_report': ('django_cfg.apps.maintenance.services', 'get_maintenance_status_report'),
    'schedule_maintenance_for_sites': ('django_cfg.apps.maintenance.services', 'schedule_maintenance_for_sites'),
    'process_scheduled_maintenances': ('django_cfg.apps.maintenance.services', 'process_scheduled_maintenances'),
}


def __getattr__(name: str):
    """Lazy import mechanism to avoid Django initialization issues."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = list(_LAZY_IMPORTS.keys())
