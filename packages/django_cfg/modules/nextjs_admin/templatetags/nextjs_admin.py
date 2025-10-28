"""
Template tags for Next.js admin integration.

Usage in templates:
    {% load nextjs_admin %}

    {% nextjs_admin_url %}                    # Get iframe URL
    {% nextjs_admin_url 'private' %}          # Get specific route URL
    {% nextjs_admin_is_enabled %}             # Check if enabled
    {% nextjs_admin_tab_title %}              # Get tab title
"""

from django import template
from django.conf import settings

register = template.Library()


def _get_config():
    """Get Next.js admin config from Django settings."""
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        return config.nextjs_admin if config and config.nextjs_admin else None
    except Exception:
        return None


@register.simple_tag
def nextjs_admin_url(route=''):
    """
    Get Next.js admin URL for iframe src.

    In development: Returns dev_url + route
    In production: Returns static_url + route.html

    Examples:
        {% nextjs_admin_url %}                    # Dev: http://localhost:3001/private, Prod: /cfg/nextjs-admin/private
        {% nextjs_admin_url 'private' %}          # Dev: http://localhost:3001/private, Prod: /cfg/nextjs-admin/private
        {% nextjs_admin_url 'private/centrifugo' %}  # Dev: http://localhost:3001/private/centrifugo, Prod: /cfg/nextjs-admin/private/centrifugo
    """
    config = _get_config()
    if not config:
        return ''

    # Clean route
    route = route.strip().lstrip('/')

    if settings.DEBUG:
        # Development: Use dev server
        dev_url = config.get_dev_url().rstrip('/')
        iframe_route = config.get_iframe_route().lstrip('/')

        # Use provided route or default iframe_route
        final_route = route if route else iframe_route

        return f"{dev_url}/{final_route}" if final_route else dev_url
    else:
        # Production: Use Django view that serves static files with SPA routing
        iframe_route = config.get_iframe_route().lstrip('/')

        # Use provided route or default iframe_route
        final_route = route if route else iframe_route

        # Always use /cfg/nextjs-admin/ prefix (Django view handles SPA routing)
        return f"/cfg/nextjs-admin/{final_route}" if final_route else "/cfg/nextjs-admin/"


@register.simple_tag
def nextjs_admin_is_enabled():
    """
    Check if Next.js admin is enabled.

    Usage:
        {% nextjs_admin_is_enabled as is_enabled %}
        {% if is_enabled %}
            <div>Next.js Admin is enabled</div>
        {% endif %}
    """
    config = _get_config()
    return config is not None


@register.simple_tag
def nextjs_admin_tab_title():
    """
    Get Next.js admin tab title.

    Usage:
        <button>{% nextjs_admin_tab_title %}</button>
    """
    config = _get_config()
    if not config:
        return 'Next.js Admin'
    return config.get_tab_title()


@register.simple_tag
def nextjs_admin_is_dev_mode():
    """
    Check if running in development mode.

    Usage:
        {% nextjs_admin_is_dev_mode as is_dev %}
        {% if is_dev %}
            <div class="dev-warning">Development Mode</div>
        {% endif %}
    """
    return settings.DEBUG


@register.simple_tag
def nextjs_admin_iframe_sandbox():
    """
    Get iframe sandbox attribute.

    Usage:
        <iframe sandbox="{% nextjs_admin_iframe_sandbox %}"></iframe>
    """
    config = _get_config()
    if not config:
        return "allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
    return config.get_iframe_sandbox()


@register.simple_tag
def nextjs_admin_static_url():
    """
    Get static URL prefix for Next.js admin.

    Usage:
        {% nextjs_admin_static_url %}  # Returns: /cfg/nextjs-admin/
    """
    return '/cfg/nextjs-admin/'


@register.simple_tag
def has_nextjs_admin():
    """
    Check if Next.js admin is configured.

    Usage:
        {% load nextjs_admin %}
        {% if has_nextjs_admin %}
            <button>Open Next.js Admin</button>
        {% endif %}
    """
    config = _get_config()
    return config is not None


@register.simple_tag
def nextjs_external_url(route=''):
    """
    Get URL for external Next.js admin (separate tab).

    This is the same as nextjs_admin_url but with a different name
    to make template code clearer.

    Usage:
        {% nextjs_external_url %}  # Default route
        {% nextjs_external_url 'dashboard' %}  # Specific route
    """
    return nextjs_admin_url(route)
