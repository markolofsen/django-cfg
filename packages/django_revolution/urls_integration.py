"""
Django Revolution URL Integration

Automatically integrates Django Revolution URL patterns into existing Django urls.py
"""

from typing import List, Any

try:
    from django.urls import path, include

    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

from .config import get_settings
from .zones import ZoneManager
from .utils import Logger


# Get version from __init__.py safely
def get_version():
    from . import __version__

    return __version__


def get_revolution_urlpatterns() -> List[Any]:
    """
    Get URL patterns from Django Revolution zones.

    Returns:
        List of URL patterns to add to main urls.py
    """
    if not DJANGO_AVAILABLE:
        return []

    try:
        # Get Django Revolution settings
        revolution_settings = get_settings()
        zone_manager = ZoneManager(revolution_settings)

        # Get zone-specific URL patterns
        zone_patterns = zone_manager.get_zone_urls()

        # Get all apps from all zones for general API routing
        all_apps = []
        for zone_name, zone in zone_manager.zones.items():
            all_apps.extend(zone.apps)

        # Remove duplicates
        all_apps = list(set(all_apps))

        # Generate app URL patterns
        app_patterns = zone_manager.get_app_urls(all_apps)

        # Combine all patterns
        revolution_patterns = []

        # Add API endpoints under /apix/ prefix
        if app_patterns:
            revolution_patterns.append(
                path(f"{revolution_settings.api_prefix}/", include(app_patterns))
            )

        # Add zone-specific schema patterns
        revolution_patterns.extend(zone_patterns)

        return revolution_patterns

    except Exception as e:
        Logger("urls_integration").error(
            f"Failed to generate Revolution URL patterns: {e}"
        )
        return []


def integrate_into_urls(urlpatterns: List[Any]) -> List[Any]:
    """
    Integrate Django Revolution URL patterns into existing urlpatterns.

    Args:
        urlpatterns: Existing URL patterns list

    Returns:
        Updated URL patterns list with Revolution patterns
    """
    if not DJANGO_AVAILABLE:
        return urlpatterns

    try:
        # Get Revolution patterns
        revolution_patterns = get_revolution_urlpatterns()

        # Add Revolution patterns to existing patterns
        urlpatterns.extend(revolution_patterns)

        Logger("urls_integration").success(
            f"Integrated {len(revolution_patterns)} Revolution URL patterns"
        )

        return urlpatterns

    except Exception as e:
        Logger("urls_integration").error(
            f"Failed to integrate Revolution patterns: {e}"
        )
        return urlpatterns


def get_revolution_urls_info() -> dict:
    """
    Get information about Django Revolution URL patterns.

    Returns:
        Dictionary with URL information
    """
    if not DJANGO_AVAILABLE:
        return {}

    try:
        revolution_settings = get_settings()
        zone_manager = ZoneManager(revolution_settings)

        # Get all apps from zones
        all_apps = []
        zone_info = {}

        for zone_name, zone in zone_manager.zones.items():
            zone_apps = zone.apps
            all_apps.extend(zone_apps)
            zone_info[zone_name] = {
                "title": zone.title,
                "description": zone.description,
                "apps": zone_apps,
                "app_count": len(zone_apps),
                "schema_url": f"/schema/{zone_name}/",
                "swagger_url": f"/schema/{zone_name}/swagger/",
            }

        # Remove duplicates
        all_apps = list(set(all_apps))

        return {
            "version": get_version(),  # Django Revolution version
            "api_prefix": revolution_settings.api_prefix,
            "total_zones": len(zone_manager.zones),
            "total_apps": len(all_apps),
            "zones": zone_info,
            "all_apps": all_apps,
        }

    except Exception as e:
        Logger("urls_integration").error(f"Failed to get Revolution URL info: {e}")
        return {}


# Convenience function for easy import
def add_revolution_urls(urlpatterns: List[Any]) -> List[Any]:
    """
    Convenience function to add Django Revolution URLs to existing patterns.

    Usage in urls.py:
        from django_revolution.urls_integration import add_revolution_urls

        urlpatterns = [
            # ... existing patterns
        ]

        # Add Revolution patterns
        urlpatterns = add_revolution_urls(urlpatterns)
    """
    return integrate_into_urls(urlpatterns)
