"""
Base settings for maintenance extension.

Provides Cloudflare-based maintenance mode management.
"""

from pydantic import Field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BaseMaintenanceSettings(BaseExtensionSettings):
    """
    Base settings for maintenance extension.

    Features:
    - Multi-site maintenance mode
    - Cloudflare integration
    - Scheduled maintenance windows
    - Admin interface for management
    """

    # === Manifest defaults ===
    name: str = "maintenance"
    version: str = "2.0.0"
    description: str = "Multi-site maintenance mode with Cloudflare integration"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "maintenance"
    url_prefix: str = "maintenance"
    url_namespace: str = "maintenance"

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Maintenance",
            icon=Icons.BUILD,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Sites",
                    icon=Icons.CLOUD,
                    app="maintenance",
                    model="cloudflaresite",
                ),
                NavigationItem(
                    title="API Keys",
                    icon=Icons.KEY,
                    app="maintenance",
                    model="cloudflareapikey",
                ),
                NavigationItem(
                    title="Scheduled",
                    icon=Icons.SCHEDULE,
                    app="maintenance",
                    model="scheduledmaintenance",
                ),
                NavigationItem(
                    title="Logs",
                    icon=Icons.LIST_ALT,
                    app="maintenance",
                    model="maintenancelog",
                ),
            ],
        ),
    )
