"""
Custom managers for maintenance models.

Simplified managers with useful query methods.
"""

from .cloudflare_site_manager import CloudflareSiteManager, CloudflareSiteQuerySet
from .maintenance_log_manager import MaintenanceLogManager, MaintenanceLogQuerySet

__all__ = [
    'CloudflareSiteManager',
    'CloudflareSiteQuerySet',
    'MaintenanceLogManager', 
    'MaintenanceLogQuerySet',
]
