"""
Template tags: library metadata, environment info, frontend detection.
"""

import socket
from django import template
from django.conf import settings

register = template.Library()


def _is_port_available(host: str, port: int, timeout: float = 0.1, retries: int = 3, retry_delay: float = 0.05) -> bool:
    import time
    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
            if attempt < retries - 1:
                time.sleep(retry_delay)
        except Exception:
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
    return False


@register.simple_tag
def lib_name():
    from django_cfg import __version__
    from django_cfg.config import LIB_NAME
    return f"{LIB_NAME} ({__version__})"


@register.simple_tag
def lib_site_url():
    from django_cfg.config import LIB_SITE_URL
    return LIB_SITE_URL


@register.simple_tag
def lib_docs_url():
    from django_cfg.config import LIB_SITE_URL
    return LIB_SITE_URL


@register.simple_tag
def lib_health_url():
    from django_cfg.config import LIB_HEALTH_URL
    return LIB_HEALTH_URL


@register.simple_tag
def lib_subtitle():
    return "The AI-First Django Framework That Thinks For You"


@register.simple_tag
def version_update_info():
    """
    Returns dict: current_version, latest_version, update_available, update_url.

    Usage:
        {% load django_cfg_lib %}
        {% version_update_info as version %}
        {% if version.update_available %}...{% endif %}
    """
    try:
        from django_cfg.core.integration.version_checker import get_version_info
        return get_version_info()
    except Exception:
        return {'current_version': None, 'latest_version': None, 'update_available': False, 'update_url': None}


@register.simple_tag
def project_name():
    from django_cfg.config import LIB_NAME
    from django_cfg.core.state import get_current_config
    config = get_current_config()
    if config and hasattr(config, 'project_name'):
        return config.project_name
    return LIB_NAME


@register.simple_tag
def is_dev():
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        return config and config.is_development
    except Exception:
        return False


@register.simple_tag
def is_frontend_dev_mode():
    if not settings.DEBUG:
        return False
    return _is_port_available('localhost', 3000) or _is_port_available('localhost', 3777)


@register.simple_tag
def nextjs_admin_url(path=''):
    path = path.strip('/')
    if not settings.DEBUG:
        return f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'
    if _is_port_available('localhost', 3777):
        base_url = 'http://localhost:3777/admin'
        return f'{base_url}/{path}' if path else base_url
    return f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'


@register.simple_tag
def has_nextjs_external_admin():
    """DEPRECATED. Always returns False."""
    return False


@register.simple_tag
def nextjs_external_admin_url(route=''):
    """DEPRECATED. Always returns empty string."""
    return ''


@register.simple_tag
def nextjs_external_admin_title():
    """DEPRECATED. Always returns empty string."""
    return ''
