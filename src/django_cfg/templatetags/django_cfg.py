"""
Django-CFG Template Tags

Provides template tags for accessing django-cfg configuration constants.
"""

from django import template

register = template.Library()


@register.simple_tag
def lib_name():
    """Get the library name."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_NAME
    from django_cfg import __version__
    return f"{LIB_NAME} ({__version__})"


@register.simple_tag
def lib_site_url():
    """Get the library site URL."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_SITE_URL
    return LIB_SITE_URL


@register.simple_tag
def lib_health_url():
    """Get the library health URL."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_HEALTH_URL
    return LIB_HEALTH_URL


@register.simple_tag
def project_name():
    """Get the project name from current config."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.core.config import get_current_config
    from django_cfg.config import LIB_NAME
    
    # Try to get project name from current config
    config = get_current_config()
    if config and hasattr(config, 'project_name'):
        return config.project_name
    
    # Fallback to library name
    return LIB_NAME
