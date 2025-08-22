"""
Django CFG URL integration utilities.

Provides automatic URL registration for django_cfg endpoints and integrations.
"""

from typing import List
from django.urls import path, include, URLPattern


def add_django_cfg_urls(urlpatterns: List[URLPattern], cfg_prefix: str = "cfg/") -> List[URLPattern]:
    """
    Automatically add django_cfg URLs and all integrations to the main URL configuration.
    
    This function adds:
    - Django CFG management URLs (cfg/)
    - Django Revolution URLs (if available)
    - Debug output (if development environment)
    
    Args:
        urlpatterns: Existing URL patterns list
        cfg_prefix: URL prefix for django_cfg endpoints (default: "cfg/")
        
    Returns:
        Updated URL patterns list with all URLs added
        
    Example:
        # In your main urls.py
        from django_cfg import add_django_cfg_urls
        
        urlpatterns = [
            path("", home_view, name="home"),
            path("admin/", admin.site.urls),
        ]
        
        # Automatically adds:
        # - path("cfg/", include("django_cfg.api.urls"))
        # - Django Revolution URLs (if available)
        # - Debug output (if development environment)
        urlpatterns = add_django_cfg_urls(urlpatterns)
    """
    # Add django_cfg API URLs
    new_patterns = urlpatterns + [
        path(cfg_prefix, include("django_cfg.api.urls")),
    ]
    
    # Try to add Django Revolution URLs if available
    try:
        from django_revolution import add_revolution_urls
        new_patterns = add_revolution_urls(new_patterns)
    except ImportError:
        # Django Revolution not available - skip
        pass
    
    # Show debug output if in development environment
    try:
        from django_cfg.core.environment import EnvironmentDetector
        if EnvironmentDetector.is_development():
            _print_url_integration_info()
    except ImportError:
        # Fallback to Django DEBUG setting
        try:
            from django.conf import settings
            if getattr(settings, 'DEBUG', False):
                _print_url_integration_info()
        except ImportError:
            pass
    
    return new_patterns


def get_django_cfg_urls_info() -> dict:
    """
    Get information about django_cfg URL integration and all integrations.
    
    Returns:
        Dictionary with complete URL integration info
    """
    try:
        from django_cfg import __version__
        version = __version__
    except ImportError:
        version = "unknown"
    
    info = {
        "django_cfg": {
            "version": version,
            "prefix": "cfg/",
            "endpoints": [
                "cfg/commands/",
                "cfg/dashboard/",
                "cfg/status/",
            ],
            "description": "Django CFG management endpoints",
        }
    }
    
    # Add Django Revolution info if available
    try:
        from django_revolution import get_revolution_urls_info
        revolution_info = get_revolution_urls_info()
        if revolution_info:
            info["django_revolution"] = revolution_info
    except ImportError:
        pass
    
    return info


def _print_url_integration_info():
    """Print URL integration debug information."""
    integration_info = get_django_cfg_urls_info()
    
    print("=" * 60)
    
    # Django CFG info
    if "django_cfg" in integration_info:
        cfg_info = integration_info["django_cfg"]
        print("⚙️  Django CFG URL Integration")
        print(f"📦 Version: {cfg_info.get('version', 'unknown')}")
        print(f"🔗 Prefix: /{cfg_info.get('prefix', 'cfg/')}")
        print(f"📋 Endpoints: {len(cfg_info.get('endpoints', []))}")
        for endpoint in cfg_info.get('endpoints', []):
            print(f"   • {endpoint}")
        print("=" * 60)
    
    # Django Revolution info
    if "django_revolution" in integration_info:
        revolution_info = integration_info["django_revolution"]
        print("🚀 Django Revolution URL Integration")
        print(f"📦 Version: {revolution_info.get('version', 'unknown')}")
        print(f"📊 Zones: {revolution_info.get('total_zones', 0)}")
        print(f"📱 Apps: {revolution_info.get('total_apps', 0)}")
        print(f"🔗 API Prefix: /{revolution_info.get('api_prefix', 'apix')}/")
        print("=" * 60)
