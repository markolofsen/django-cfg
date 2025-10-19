"""
Django Client (OpenAPI) integration callbacks.
"""

import logging
from typing import Any, Dict, List, Tuple

from django.conf import settings

logger = logging.getLogger(__name__)


class OpenAPIClientCallbacks:
    """Django Client (OpenAPI) integration callbacks."""

    def get_openapi_groups_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Get Django Client (OpenAPI) groups data."""
        try:
            # Get groups from OpenAPI service (includes default cfg group)
            from django_cfg.modules.django_client.core import get_openapi_service

            service = get_openapi_service()
            if not service.config:
                return [], {"total_apps": 0, "total_endpoints": 0, "total_groups": 0}

            # Get groups with defaults (includes cfg group automatically)
            groups_dict = service.get_groups()
            groups_list = list(groups_dict.values())
            api_prefix = getattr(service.config, "api_prefix", "api")

            # Ensure urlconf modules AND URL patterns are created for all groups with apps
            try:
                from django.urls import path
                from drf_spectacular.views import SpectacularAPIView
                from django_cfg.modules.django_client.core.groups import GroupManager
                from django_cfg.modules.django_client import urls as client_urls

                manager = GroupManager(service.config)
                for group in groups_list:
                    group_name = getattr(group, "name", "unknown") if not isinstance(group, dict) else group.get("name", "unknown")
                    apps = getattr(group, "apps", []) if not isinstance(group, dict) else group.get("apps", [])
                    group_version = getattr(group, "version", "1.0.0") if not isinstance(group, dict) else group.get("version", "1.0.0")

                    if apps:
                        try:
                            # Create urlconf module
                            manager.create_urlconf_module(group_name)

                            # Check if URL pattern already exists
                            url_name = f'openapi-schema-{group_name}'
                            url_exists = any(
                                hasattr(pattern, 'name') and pattern.name == url_name
                                for pattern in client_urls.urlpatterns
                            )

                            # Add URL pattern if it doesn't exist
                            if not url_exists:
                                new_pattern = path(
                                    f'{group_name}/schema/',
                                    SpectacularAPIView.as_view(
                                        urlconf=f'_django_client_urlconf_{group_name}',
                                        api_version=group_version,
                                    ),
                                    name=url_name,
                                )
                                client_urls.urlpatterns.append(new_pattern)
                        except Exception:
                            pass  # Silently skip if already exists or fails
            except Exception:
                pass  # Silently skip if GroupManager fails

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
                    "schema_url": f"/cfg/openapi/{group_name}/schema/",
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
