"""
Django CFG URL integration utilities.

Provides automatic URL registration for django_cfg endpoints and integrations.
"""

import importlib
import sys
from typing import List, Set

from django.conf import settings
from django.conf.urls.static import static
from django.urls import URLPattern, include, path
from django.views.static import serve


def _get_openapi_group_urls() -> List[URLPattern]:
    """
    Automatically generate URL patterns from OpenAPI groups.

    For each OpenAPI group defined in config:
    1. Get the group from OpenAPI service
    2. Get the apps for that group
    3. For each app with urls.py, include it
    4. Add path("{api_prefix}/{app_basename}/", include("{app}.urls"))

    Returns:
        List of URL patterns for OpenAPI groups
    """
    patterns = []

    try:
        from django_cfg.modules.django_client.core import get_openapi_service

        service = get_openapi_service()

        # Check if OpenAPI client is configured and enabled
        if not service.config or not service.is_enabled():
            return patterns

        # Get API prefix from config (default: "api")
        api_prefix = getattr(service.config, 'api_prefix', 'api') or 'api'
        api_prefix = api_prefix.rstrip('/')  # Remove trailing slash

        # Track already added apps to avoid duplicates
        added_apps: Set[str] = set()

        # Get all groups from config
        for group_config in service.config.groups:
            group_name = group_config.name

            # Skip the internal "cfg" group - it's handled separately
            if group_name == "cfg":
                continue

            # Get apps for this group
            apps = group_config.apps

            # Process each app in the group
            for app_name in apps:
                # Skip if already added
                if app_name in added_apps:
                    continue

                # Check if the app has a urls.py module
                try:
                    urls_module = f"{app_name}.urls"
                    importlib.import_module(urls_module)

                    # Get the app basename (last part of the app path)
                    # e.g., "apps.workspaces" -> "workspaces"
                    app_basename = app_name.split('.')[-1]

                    # Add URL pattern for this app
                    url_pattern = f"{api_prefix}/{app_basename}/"
                    patterns.append(path(url_pattern, include(urls_module)))
                    added_apps.add(app_name)

                    # Log successful auto-registration
                    sys.stderr.write(f"✅ Auto-registered URL: /{url_pattern} -> {urls_module}\n")
                    sys.stderr.flush()

                except ImportError as e:
                    # App doesn't have urls.py - skip it
                    sys.stderr.write(f"⚠️  Skipping {app_name}: {e}\n")
                    sys.stderr.flush()
                    continue

    except Exception as e:
        # Don't break if OpenAPI config is not available
        sys.stderr.write(f"❌ ERROR: Could not auto-add OpenAPI group URLs: {e}\n")
        sys.stderr.flush()

    return patterns


def add_django_cfg_urls(urlpatterns: List[URLPattern]) -> List[URLPattern]:
    """
    Automatically add django_cfg URLs and all integrations to the main URL configuration.

    This function adds:
    - Django CFG management URLs (/cfg/, /health/, etc.)
    - Django Client URLs (if available)
    - Static files serving (DEBUG mode only)
    - Media files serving (all environments via serve view)
    - Django Browser Reload (DEBUG mode, if installed)
    - Startup information display (based on config)

    Args:
        urlpatterns: Existing URL patterns list

    Returns:
        Updated URL patterns list with all URLs added

    Example:
        # In your main urls.py
        from django_cfg import add_django_cfg_urls

        urlpatterns = [
            path("", home_view, name="home"),
            path("admin/", admin.site.urls),
        ]

        # Automatically adds django_cfg URLs with proper prefixes
        # No need to manually configure static/media serving!
        urlpatterns = add_django_cfg_urls(urlpatterns)
    """
    # Add django_cfg API URLs
    # Note: URL prefixes (cfg/, health/, etc.) are defined in django_cfg.apps.urls
    new_patterns = urlpatterns + [
        path("", include("django_cfg.apps.urls")),
    ]

    # Automatically add OpenAPI group URLs from config
    openapi_urls = _get_openapi_group_urls()
    if openapi_urls:
        new_patterns += openapi_urls

    # Automatically add extension URLs (from extensions/ folder)
    try:
        from django_cfg.extensions.urls import get_extension_url_patterns
        extension_urls = get_extension_url_patterns(url_prefix="cfg")
        if extension_urls:
            new_patterns += extension_urls
    except Exception as e:
        sys.stderr.write(f"❌ ERROR: Could not auto-add extension URLs: {e}\n")
        sys.stderr.flush()

    # Add django-browser-reload URLs in development (if installed)
    if settings.DEBUG:
        try:
            import django_browser_reload
            new_patterns = new_patterns + [
                path("__reload__/", include("django_browser_reload.urls")),
            ]
        except ImportError:
            # django-browser-reload not installed - skip
            pass

    # Add static files serving in development
    if settings.DEBUG:
        new_patterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Add media files serving (both dev and prod)
    # Using serve view for consistent behavior across environments
    # Django will serve media files when MEDIA_ROOT is set
    # If using external CDN, requests won't reach Django anyway
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    media_url = getattr(settings, 'MEDIA_URL', None)

    if media_root and media_url:
        from django.urls import re_path
        from urllib.parse import urlparse

        # Extract path prefix from media_url
        if media_url.startswith(('http://', 'https://', '//')):
            # Absolute URL - extract path part
            # e.g., "https://api.example.com/media/" -> "media/"
            parsed = urlparse(media_url)
            media_prefix = parsed.path.strip('/')
        else:
            # Relative URL - use directly
            media_prefix = media_url.strip('/')

        if media_prefix:
            new_patterns += [
                re_path(rf'^{media_prefix}/(?P<path>.*)$', serve, {'document_root': media_root}),
            ]

    # Show startup info based on config
    try:
        from . import print_startup_info
        print_startup_info()
    except ImportError:
        pass

    return new_patterns


def get_django_cfg_urls_info() -> dict:
    """
    Get information about django_cfg URL integration and all integrations.
    
    Returns:
        Dictionary with complete URL integration info
    """
    from django_cfg.config import (
        LIB_SITE_URL,
        LIB_GITHUB_URL,
        LIB_HEALTH_URL,
        LIB_NAME,
        LIB_SITE_URL,
        LIB_SUPPORT_URL,
    )

    try:
        from django_cfg import __version__
        version = __version__
    except ImportError:
        version = "unknown"

    # Get current config directly from Pydantic
    config = None
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
    except Exception:
        pass


    info = {
        "django_cfg": {
            "version": version,
            "prefix": "cfg/",
            "description": LIB_NAME,
            "site_url": LIB_SITE_URL,
            "docs_url": LIB_SITE_URL,
            "github_url": LIB_GITHUB_URL,
            "support_url": LIB_SUPPORT_URL,
            "health_url": LIB_HEALTH_URL,
            "env_mode": config.env_mode if config else "unknown",
            "debug": config.debug if config else False,
            "startup_info_mode": config.startup_info_mode if config else "full",
        }
    }

    # Add Django Client info if available
    try:
        from django_cfg.modules.django_client.core.config.service import DjangoOpenAPI
        service = DjangoOpenAPI.instance()
        if service.config and service.config.enabled:
            info["django_client"] = {
                "enabled": True,
                "groups": len(service.config.groups),
                "base_url": service.config.base_url,
                "output_dir": service.config.output_dir,
            }
    except ImportError:
        pass

    return info
