"""
Simplified maintenance services.

Clean imports for the service classes with lazy loading.
"""

# Lazy import registry to avoid Django initialization issues
_LAZY_IMPORTS = {
    # Services
    'MaintenanceService': ('django_cfg.apps.maintenance.services.maintenance_service', 'MaintenanceService'),
    'SiteSyncService': ('django_cfg.apps.maintenance.services.site_sync_service', 'SiteSyncService'),
    'BulkOperationsService': ('django_cfg.apps.maintenance.services.bulk_operations_service', 'BulkOperationsService'),
    'ScheduledMaintenanceService': ('django_cfg.apps.maintenance.services.scheduled_maintenance_service', 'ScheduledMaintenanceService'),
    
    # Service functions
    'enable_maintenance_for_domain': ('django_cfg.apps.maintenance.services.maintenance_service', 'enable_maintenance_for_domain'),
    'disable_maintenance_for_domain': ('django_cfg.apps.maintenance.services.maintenance_service', 'disable_maintenance_for_domain'),
    'sync_site_from_cloudflare': ('django_cfg.apps.maintenance.services.site_sync_service', 'sync_site_from_cloudflare'),
    'bulk_operations': ('django_cfg.apps.maintenance.services.bulk_operations_service', 'bulk_operations'),
    'scheduled_maintenance_service': ('django_cfg.apps.maintenance.services.scheduled_maintenance_service', 'scheduled_maintenance_service'),
    'enable_maintenance_for_domains': ('django_cfg.apps.maintenance.services.bulk_operations_service', 'enable_maintenance_for_domains'),
    'disable_maintenance_for_domains': ('django_cfg.apps.maintenance.services.bulk_operations_service', 'disable_maintenance_for_domains'),
    'bulk_sync_all_sites': ('django_cfg.apps.maintenance.services.bulk_operations_service', 'bulk_sync_all_sites'),
    'get_maintenance_status_report': ('django_cfg.apps.maintenance.services.bulk_operations_service', 'get_maintenance_status_report'),
    'schedule_maintenance_for_sites': ('django_cfg.apps.maintenance.services.scheduled_maintenance_service', 'schedule_maintenance_for_sites'),
    'process_scheduled_maintenances': ('django_cfg.apps.maintenance.services.scheduled_maintenance_service', 'process_scheduled_maintenances'),
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
