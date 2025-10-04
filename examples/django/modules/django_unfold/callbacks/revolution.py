"""
Django Revolution integration callbacks.
"""

import logging
from typing import Dict, Any, List, Tuple

from django.conf import settings

logger = logging.getLogger(__name__)


class RevolutionCallbacks:
    """Django Revolution integration callbacks."""
    
    def get_revolution_zones_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Get Django Revolution zones data."""
        try:
            # Try to get revolution config from Django settings
            revolution_config = getattr(settings, "DJANGO_REVOLUTION", {})
            zones = revolution_config.get("zones", {})
            api_prefix = revolution_config.get("api_prefix", "apix")

            zones_data = []
            total_apps = 0
            total_endpoints = 0

            for zone_name, zone_config in zones.items():
                # Handle both dict and object access
                if isinstance(zone_config, dict):
                    title = zone_config.get("title", zone_name.title())
                    description = zone_config.get("description", f"{zone_name} zone")
                    apps = zone_config.get("apps", [])
                    public = zone_config.get("public", False)
                    auth_required = zone_config.get("auth_required", True)
                else:
                    # Handle object access (for ZoneConfig instances)
                    title = getattr(zone_config, "title", zone_name.title())
                    description = getattr(zone_config, "description", f"{zone_name} zone")
                    apps = getattr(zone_config, "apps", [])
                    public = getattr(zone_config, "public", False)
                    auth_required = getattr(zone_config, "auth_required", True)

                # Count actual endpoints by checking URL patterns (simplified estimate)
                endpoint_count = len(apps) * 3  # Conservative estimate

                zones_data.append({
                    "name": zone_name,
                    "title": title,
                    "description": description,
                    "app_count": len(apps),
                    "endpoint_count": endpoint_count,
                    "status": "active",
                    "public": public,
                    "auth_required": auth_required,
                    "schema_url": f"/schema/{zone_name}/schema/",
                    "swagger_url": f"/schema/{zone_name}/schema/swagger/",
                    "redoc_url": f"/schema/{zone_name}/redoc/",
                    "api_url": f"/{api_prefix}/{zone_name}/",
                })

                total_apps += len(apps)
                total_endpoints += endpoint_count

            return zones_data, {
                "total_apps": total_apps,
                "total_endpoints": total_endpoints,
                "total_zones": len(zones),
            }
        except Exception as e:
            logger.error(f"Error getting revolution zones: {e}")
            return [], {
                "total_apps": 0,
                "total_endpoints": 0,
                "total_zones": 0,
            }
