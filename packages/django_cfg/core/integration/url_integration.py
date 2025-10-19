"""
Django CFG URL integration utilities.

Provides automatic URL registration for django_cfg endpoints and integrations.
"""

from typing import List

from django.conf import settings
from django.conf.urls.static import static
from django.urls import URLPattern, include, path
from django.views.static import serve


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
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        # Remove leading slash from MEDIA_URL for path()
        media_prefix = settings.MEDIA_URL.lstrip('/')
        new_patterns += [
            path(f"{media_prefix}<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
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
        LIB_DOCS_URL,
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
            "docs_url": LIB_DOCS_URL,
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
