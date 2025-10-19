"""
Django URL integration.

Provides URL patterns for OpenAPI schema generation.
Each configured group gets its own schema endpoint.
"""

from typing import Any, List


def _is_django_configured() -> bool:
    """Check if Django settings are configured."""
    try:
        from django.conf import settings
        return settings.configured
    except ImportError:
        return False


def get_openapi_urls() -> List[Any]:
    """
    Get URL patterns for OpenAPI schema generation.

    Creates URLs for each configured group:
    - /openapi/{group_name}/schema/ - JSON schema

    Returns:
        List of Django URL patterns
    """
    try:
        from django.urls import path
        from drf_spectacular.views import SpectacularAPIView

        from django_cfg.modules.django_client.core import get_openapi_service
    except ImportError:
        return []

    service = get_openapi_service()

    if not service.config or not service.is_enabled():
        return []

    patterns = []

    for group_name in service.get_group_names():
        group_config = service.get_group(group_name)
        if not group_config:
            continue

        # Schema endpoint for each group
        patterns.append(
            path(
                f'{group_name}/schema/',
                SpectacularAPIView.as_view(
                    urlconf=f'_django_client_urlconf_{group_name}',
                    api_version=group_config.version,
                ),
                name=f'openapi-schema-{group_name}',
            )
        )

    return patterns


# Export urlpatterns for django.urls.include()
# Only create urlpatterns if Django is configured
if _is_django_configured():
    urlpatterns = get_openapi_urls()
else:
    urlpatterns = []


__all__ = ["get_openapi_urls", "urlpatterns"]
