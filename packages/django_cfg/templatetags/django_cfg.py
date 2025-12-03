"""
Django-CFG Template Tags

Provides template tags for accessing django-cfg configuration constants.
"""

import os
import socket
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from rest_framework_simplejwt.tokens import RefreshToken

register = template.Library()


def _is_port_available(host: str, port: int, timeout: float = 0.1, retries: int = 3, retry_delay: float = 0.05) -> bool:
    """
    Check if a port is available (listening) on the specified host with retry logic.

    Performs multiple connection attempts with delays to handle dev servers
    that may be compiling or starting up (e.g., Next.js first request).

    Args:
        host: Host to check (e.g., 'localhost', '127.0.0.1')
        port: Port number to check
        timeout: Connection timeout in seconds per attempt (default: 0.1s)
        retries: Number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 0.05s)

    Returns:
        bool: True if port is available, False otherwise

    Example:
        # Quick check (default): ~0.4s max (3 attempts × 0.1s + 2 × 0.05s delay)
        _is_port_available('localhost', 3000)

        # Patient check for slow servers
        _is_port_available('localhost', 3000, timeout=0.5, retries=5)
    """
    import time

    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return True  # Success - port is available

            # Port not available, retry if not last attempt
            if attempt < retries - 1:
                time.sleep(retry_delay)

        except Exception:
            # Connection error, retry if not last attempt
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue

    return False  # All retries failed


@register.simple_tag
def lib_name():
    """Get the library name."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg import __version__
    from django_cfg.config import LIB_NAME
    return f"{LIB_NAME} ({__version__})"


@register.simple_tag
def version_update_info():
    """
    Get version update information from PyPI.

    Returns a dict with:
    - current_version: installed version
    - latest_version: latest on PyPI
    - update_available: bool
    - update_url: PyPI URL

    Cached for 1 hour to avoid excessive API calls.

    Usage in template:
        {% load django_cfg %}
        {% version_update_info as version %}
        {% if version.update_available %}
            Update: {{ version.current_version }} → {{ version.latest_version }}
        {% endif %}
    """
    try:
        from django_cfg.core.integration.version_checker import get_version_info
        return get_version_info()
    except Exception:
        return {
            'current_version': None,
            'latest_version': None,
            'update_available': False,
            'update_url': None,
        }


@register.simple_tag
def lib_site_url():
    """Get the library site URL."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_SITE_URL
    return LIB_SITE_URL


@register.simple_tag
def lib_docs_url():
    """Get the library documentation URL."""
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
def is_dev():
    """
    Check if project is in development mode.

    Returns True if the current DjangoConfig has is_development = True.

    Usage in template:
        {% load django_cfg %}
        {% is_dev as is_development %}
        {% if is_development %}
            <div>Development Mode</div>
        {% endif %}
    """
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        return config and config.is_development
    except Exception:
        return False


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

    In DEBUG mode, always returns dev server URL. Client-side JavaScript
    will handle fallback to static files if dev server is unavailable.

    Returns:
        - DEBUG=True: http://localhost:3777/admin/{path}
        - DEBUG=False: /cfg/admin/admin/{path}

    Note: Port 3000 is reserved for external Next.js admin (Tab 2).
    Both tabs use /admin route for consistency.

    Usage in template:
        {% load django_cfg %}
        <iframe src="{% nextjs_admin_url %}"></iframe>
        <iframe src="{% nextjs_admin_url 'crypto' %}"></iframe>
    """
    # Normalize path - remove leading/trailing slashes
    path = path.strip('/')

    if not settings.DEBUG:
        # Production mode: always use static files with /admin route
        return f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'

    # Check if port 3777 is available for Tab 1 (built-in admin)
    port_3777_available = _is_port_available('localhost', 3777)

    if port_3777_available:
        # Dev server is running on 3777 - use /admin route for consistency
        base_url = 'http://localhost:3777/admin'
        return f'{base_url}/{path}' if path else base_url
    else:
        # No dev server - use static files with /admin route
        return f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'


@register.simple_tag
def is_frontend_dev_mode():
    """
    Check if frontend is in development mode.

    Auto-detects by checking:
        - DEBUG=True
        - AND (port 3000 OR port 3777 is available)

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
            _is_port_available('localhost', 3777))


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

    In DEBUG mode, always returns dev server URL. Client-side JavaScript
    will handle fallback to static files if dev server is unavailable.

    Returns:
        - DEBUG=True: http://localhost:3000/admin/{route}
        - DEBUG=False: /cfg/nextjs-admin/admin/{route}

    This is for the external admin panel (solution project).

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

        # Auto-detect development mode: DEBUG=True + port 3000 available
        if settings.DEBUG and _is_port_available('localhost', 3000):
            # Development mode: solution project on port 3000
            # Routes start with /admin in Next.js (e.g., /admin, /admin/crypto)
            base_url = 'http://localhost:3000/admin'
            return f'{base_url}/{route}' if route else base_url
        else:
            # Production mode: use relative URL - Django serves from extracted ZIP with /admin prefix
            return f"/cfg/nextjs-admin/admin/{route}" if route else "/cfg/nextjs-admin/admin/"
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


@register.simple_tag(takes_context=True)
def generate_jwt_tokens(context):
    """
    Generate JWT tokens for the current authenticated user.

    Returns a dict with 'access' and 'refresh' tokens for use in templates.

    Usage:
        {% load django_cfg %}
        {% generate_jwt_tokens as jwt_tokens %}
        localStorage.setItem('auth_token', '{{ jwt_tokens.access }}');
        localStorage.setItem('refresh_token', '{{ jwt_tokens.refresh }}');
    """
    from django.contrib.auth.models import AnonymousUser

    request = context.get('request')
    if not request:
        return {'access': '', 'refresh': ''}

    user = getattr(request, 'user', None)
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return {'access': '', 'refresh': ''}

    try:
        # Generate tokens for the authenticated user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return {
            'access': access_token,
            'refresh': refresh_token
        }
    except ImportError:
        return {'access': '', 'refresh': ''}
    except Exception as e:
        return {'access': '', 'refresh': ''}
