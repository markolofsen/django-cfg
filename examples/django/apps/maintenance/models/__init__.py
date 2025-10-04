"""
Simplified maintenance models.

Clean imports for the 4 models, properly decomposed.
Uses lazy imports to avoid Django initialization issues.
"""

# Lazy import registry to avoid Django initialization issues
_LAZY_IMPORTS = {
    'CloudflareApiKey': ('django_cfg.apps.maintenance.models.cloudflare_api_key', 'CloudflareApiKey'),
    'CloudflareSite': ('django_cfg.apps.maintenance.models.cloudflare_site', 'CloudflareSite'),
    'MaintenanceLog': ('django_cfg.apps.maintenance.models.maintenance_log', 'MaintenanceLog'),
    'ScheduledMaintenance': ('django_cfg.apps.maintenance.models.scheduled_maintenance', 'ScheduledMaintenance'),
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
