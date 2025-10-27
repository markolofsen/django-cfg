"""
API Zones Service

OpenAPI zones/groups management and introspection.
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class APIZonesService:
    """
    Service for OpenAPI zones (groups) management.

    %%PRIORITY:MEDIUM%%
    %%AI_HINT: Manages OpenAPI schema groups and endpoints%%

    TAGS: openapi, api, zones, groups, service
    """

    def __init__(self):
        """Initialize API zones service."""
        self.logger = logger

    def get_zones_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get OpenAPI zones (groups) data.

        Returns:
            Tuple of (zones_list, summary_dict)

        %%AI_HINT: Integrates with django_client module if available%%
        """
        try:
            # Try to import django_client service
            from django_cfg.modules.django_client.core import get_openapi_service

            service = get_openapi_service()
            if not service.config:
                return [], {"total_apps": 0, "total_endpoints": 0, "total_zones": 0}

            # Get groups (zones)
            groups_dict = service.get_groups()
            groups_list = list(groups_dict.values())
            api_prefix = getattr(service.config, "api_prefix", "api")

            zones_data = []
            total_apps = 0
            total_endpoints = 0

            for group in groups_list:
                # Handle both dict and object access
                if isinstance(group, dict):
                    zone_name = group.get("name", "unknown")
                    title = group.get("title", zone_name.title())
                    description = group.get("description", f"{zone_name} zone")
                    apps = group.get("apps", [])
                else:
                    zone_name = getattr(group, "name", "unknown")
                    title = getattr(group, "title", zone_name.title())
                    description = getattr(group, "description", f"{zone_name} zone")
                    apps = getattr(group, "apps", [])

                # Estimate endpoint count
                endpoint_count = len(apps) * 3

                zones_data.append({
                    "name": zone_name,
                    "title": title,
                    "description": description,
                    "app_count": len(apps),
                    "endpoint_count": endpoint_count,
                    "status": "active" if apps else "empty",
                    "schema_url": f"/cfg/openapi/{zone_name}/schema/",
                    "api_url": f"/{api_prefix}/{zone_name}/",
                    "apps": apps,
                })

                total_apps += len(apps)
                total_endpoints += endpoint_count

            summary = {
                "total_apps": total_apps,
                "total_endpoints": total_endpoints,
                "total_zones": len(zones_data),
            }

            return zones_data, summary

        except ImportError:
            self.logger.warning("django_client module not available")
            return [], {"total_apps": 0, "total_endpoints": 0, "total_zones": 0}
        except Exception as e:
            self.logger.error(f"Error getting zones data: {e}")
            return [], {"total_apps": 0, "total_endpoints": 0, "total_zones": 0}

    def get_zones_summary(self) -> Dict[str, Any]:
        """
        Get summary of all API zones.

        Returns:
            Dictionary with zones list and summary statistics
        """
        try:
            zones_list, summary = self.get_zones_data()

            return {
                "zones": zones_list,
                "summary": summary,
            }

        except Exception as e:
            self.logger.error(f"Error getting zones summary: {e}")
            return {
                "zones": [],
                "summary": {"total_apps": 0, "total_endpoints": 0, "total_zones": 0},
            }
