"""
Django Client (OpenAPI) integration callbacks.
"""

import logging
from typing import Dict, Any, List, Tuple

from django.conf import settings

logger = logging.getLogger(__name__)


class OpenAPIClientCallbacks:
    """Django Client (OpenAPI) integration callbacks."""

    def get_openapi_groups_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Get Django Client (OpenAPI) groups data."""
        try:
            # Try to get openapi_client config from Django settings
            openapi_config = getattr(settings, "OPENAPI_CLIENT", {})
            if isinstance(openapi_config, dict):
                groups_list = openapi_config.get("groups", [])
                api_prefix = openapi_config.get("api_prefix", "api")
            else:
                # Handle Pydantic model instance
                groups_list = getattr(openapi_config, "groups", [])
                api_prefix = getattr(openapi_config, "api_prefix", "api")

            groups_data = []
            total_apps = 0
            total_endpoints = 0

            for group in groups_list:
                # Handle both dict and object access
                if isinstance(group, dict):
                    group_name = group.get("name", "unknown")
                    title = group.get("title", group_name.title())
                    description = group.get("description", f"{group_name} group")
                    apps = group.get("apps", [])
                else:
                    # Handle object access (for OpenAPIGroupConfig instances)
                    group_name = getattr(group, "name", "unknown")
                    title = getattr(group, "title", group_name.title())
                    description = getattr(group, "description", f"{group_name} group")
                    apps = getattr(group, "apps", [])

                # Count actual endpoints by checking URL patterns (simplified estimate)
                endpoint_count = len(apps) * 3  # Conservative estimate

                groups_data.append({
                    "name": group_name,
                    "title": title,
                    "description": description,
                    "app_count": len(apps),
                    "endpoint_count": endpoint_count,
                    "status": "active",
                    "schema_url": f"/schema/{group_name}/",
                    "swagger_url": f"/schema/{group_name}/swagger/",
                    "redoc_url": f"/schema/{group_name}/redoc/",
                    "api_url": f"/{api_prefix}/{group_name}/",
                })

                total_apps += len(apps)
                total_endpoints += endpoint_count

            return groups_data, {
                "total_apps": total_apps,
                "total_endpoints": total_endpoints,
                "total_groups": len(groups_list),
            }
        except Exception as e:
            logger.error(f"Error getting OpenAPI groups: {e}")
            return [], {
                "total_apps": 0,
                "total_endpoints": 0,
                "total_groups": 0,
            }


# Keep backward compatibility alias
RevolutionCallbacks = OpenAPIClientCallbacks
