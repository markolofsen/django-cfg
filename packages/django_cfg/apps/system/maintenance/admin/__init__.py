"""
Maintenance admin interfaces using Django-CFG admin system.

Refactored admin interfaces with Material Icons and optimized queries.
"""

from .api_key_admin import CloudflareApiKeyAdmin
from .log_admin import MaintenanceLogAdmin
from .scheduled_admin import ScheduledMaintenanceAdmin
from .site_admin import CloudflareSiteAdmin

__all__ = [
    'CloudflareApiKeyAdmin',
    'CloudflareSiteAdmin',
    'MaintenanceLogAdmin',
    'ScheduledMaintenanceAdmin',
]
