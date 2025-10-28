"""
Django-CFG Template Tags

Provides template tags for accessing django-cfg configuration constants.
"""

import os
import socket
import time
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from rest_framework_simplejwt.tokens import RefreshToken

register = template.Library()


def _is_port_available(host: str, port: int, timeout: float = 0.1) -> bool:
    """
    Check if a port is available (listening) on the specified host.

    Uses a quick socket connection test with minimal timeout.
    Returns True if the port is open and accepting connections.

    Args:
        host: Host to check (e.g., 'localhost', '127.0.0.1')
        port: Port number to check
        timeout: Connection timeout in seconds (default: 0.1s)

    Returns:
        bool: True if port is available, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


@register.simple_tag
def lib_name():
    """Get the library name."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg import __version__
    from django_cfg.config import LIB_NAME
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
def lib_subtitle():
    """Get the library subtitle/tagline."""
    return "The AI-First Django Framework That Thinks For You"


@register.simple_tag
def project_name():
    """Get the project name from current config."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_NAME
    from django_cfg.core.state import get_current_config

    # Try to get project name from current config
    config = get_current_config()
    if config and hasattr(config, 'project_name'):
        return config.project_name

    # Fallback to library name
    return LIB_NAME


@register.simple_tag(takes_context=True)
def user_jwt_token(context):
    """
    Generate JWT access token for the current authenticated user.

    Returns JWT token that can be used for API authentication.
    Uses Authorization: Bearer <token> header.

    Usage in template:
        {% load django_cfg %}
        <script>
            window.USER_JWT_TOKEN = '{% user_jwt_token %}';
        </script>
    """
    request = context.get('request')
    if not request or not request.user or not request.user.is_authenticated:
        return ''

    refresh = RefreshToken.for_user(request.user)
    return str(refresh.access_token)


@register.simple_tag(takes_context=True)
def user_jwt_refresh_token(context):
    """
    Generate JWT refresh token for the current authenticated user.

    Returns JWT refresh token that can be used to obtain new access tokens.

    Usage in template:
        {% load django_cfg %}
        <script>
            window.USER_JWT_REFRESH_TOKEN = '{% user_jwt_refresh_token %}';
        </script>
    """
    request = context.get('request')
    if not request or not request.user or not request.user.is_authenticated:
        return ''

    refresh = RefreshToken.for_user(request.user)
    return str(refresh)


@register.simple_tag(takes_context=True)
def inject_jwt_tokens_script(context):
    """
    Generate complete script tag that injects JWT tokens into localStorage.

    Automatically stores auth_token and refresh_token in localStorage
    for the current authenticated user.

    Usage in template (usually in <head> or before </body>):
        {% load django_cfg %}
        {% inject_jwt_tokens_script %}
    """
    request = context.get('request')
    if not request or not request.user or not request.user.is_authenticated:
        return ''

    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    script = f"""<script>
(function() {{
    try {{
        // Store JWT tokens in localStorage for Next.js app
        localStorage.setItem('auth_token', '{access_token}');
        localStorage.setItem('refresh_token', '{refresh_token}');
        console.log('JWT tokens injected successfully');
    }} catch (e) {{
        console.error('Failed to inject JWT tokens:', e);
    }}
}})();
</script>"""
    return mark_safe(script)


@register.simple_tag
def nextjs_admin_url(path=''):
    """
    Get the URL for Next.js Admin Panel (Built-in Dashboard - Tab 1).

    Auto-detects development mode with priority:
        1. If port 3001 is available → http://localhost:3001/admin/{path} (dev server)
        2. Otherwise → /cfg/admin/admin/{path} (static files)

    Note: Port 3000 is reserved for external Next.js admin (Tab 2).

    Usage in template:
        {% load django_cfg %}
        <iframe src="{% nextjs_admin_url %}"></iframe>
        <iframe src="{% nextjs_admin_url 'centrifugo' %}"></iframe>
    """
    # Normalize path - remove leading/trailing slashes
    path = path.strip('/')

    # Add cache busting parameter (timestamp in milliseconds)
    cache_buster = f'_={int(time.time() * 1000)}'

    if not settings.DEBUG:
        # Production mode: always use static files with cache buster
        base_url = f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'
        return f'{base_url}?{cache_buster}'

    # Check if port 3001 is available for Tab 1 (built-in admin)
    port_3001_available = _is_port_available('localhost', 3001)

    if port_3001_available:
        # Dev server is running on 3001 - use it
        base_url = 'http://localhost:3001/admin'
        url = f'{base_url}/{path}' if path else base_url
        return f'{url}?{cache_buster}'
    else:
        # No dev server or dev server stopped - use static files with cache buster
        base_url = f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'
        return f'{base_url}?{cache_buster}'


@register.simple_tag
def is_frontend_dev_mode():
    """
    Check if frontend is in development mode.

    Auto-detects by checking:
        - DEBUG=True
        - AND (port 3000 OR port 3001 is available)

    Returns True if any Next.js dev server is detected.

    Usage in template:
        {% load django_cfg %}
        {% if is_frontend_dev_mode %}
            <div class="dev-badge">Dev Mode</div>
        {% endif %}
    """
    if not settings.DEBUG:
        return False

    # Check if either dev server is running
    return (_is_port_available('localhost', 3000) or
            _is_port_available('localhost', 3001))


@register.simple_tag
def has_nextjs_external_admin():
    """
    Check if external Next.js admin is configured.

    Returns True if NextJsAdminConfig is set in Django config.

    Usage in template:
        {% load django_cfg %}
        {% has_nextjs_external_admin as is_enabled %}
        {% if is_enabled %}
            <div>External Next.js Admin Available</div>
        {% endif %}
    """
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        return config and config.nextjs_admin is not None
    except Exception:
        return False


@register.simple_tag
def nextjs_external_admin_url(route=''):
    """
    Get URL for external Next.js admin (Tab 2 - solution project).

    Auto-detects development mode:
        - If DEBUG=True AND localhost:3000 is available → http://localhost:3000/admin/{route}
        - Otherwise → /cfg/nextjs-admin/admin/{route} (static files)

    This is for the external admin panel (solution project).
    No env variable needed - automatically detects running dev server!

    Usage in template:
        {% load django_cfg %}
        <iframe src="{% nextjs_external_admin_url %}"></iframe>
        <iframe src="{% nextjs_external_admin_url 'dashboard' %}"></iframe>
    """
    try:
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        if not config or not config.nextjs_admin:
            return ''

        route = route.strip('/')

        # Add cache busting parameter (timestamp in milliseconds)
        cache_buster = f'_={int(time.time() * 1000)}'

        # Auto-detect development mode: DEBUG=True + port 3000 available
        if settings.DEBUG and _is_port_available('localhost', 3000):
            # Development mode: solution project on port 3000
            base_url = 'http://localhost:3000/admin'
            url = f'{base_url}/{route}' if route else base_url
            return f'{url}?{cache_buster}'
        else:
            # Production mode: use relative URL - Django serves from extracted ZIP with /admin prefix
            base_url = f"/cfg/nextjs-admin/admin/{route}" if route else "/cfg/nextjs-admin/admin/"
            return f'{base_url}?{cache_buster}'
    except Exception:
        return ''


@register.simple_tag
def nextjs_external_admin_title():
    """
    Get tab title for external Next.js admin.

    Returns custom title from config or default "Next.js Admin".

    Usage in template:
        {% load django_cfg %}
        <button>{% nextjs_external_admin_title %}</button>
    """
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        if not config or not config.nextjs_admin:
            return 'Next.js Admin'
        return config.nextjs_admin.get_tab_title()
    except Exception:
        return 'Next.js Admin'
