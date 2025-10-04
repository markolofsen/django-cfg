"""
Django Tailwind Layouts templatetags.

Template tags for universal Tailwind layouts with dark mode support.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# Library metadata
LIBRARY_INFO = {
    'name': 'Django Tailwind Layouts',
    'version': '1.0.0',
    'description': 'Universal Tailwind CSS layouts with dark mode for Django applications',
    'url': 'https://github.com/yourusername/django-cfg',
    'author': 'Django-CFG Team',
    'license': 'MIT',
}


@register.simple_tag
def tailwind_lib_name():
    """Get library name."""
    return LIBRARY_INFO['name']


@register.simple_tag
def tailwind_lib_version():
    """Get library version."""
    return LIBRARY_INFO['version']


@register.simple_tag
def tailwind_lib_description():
    """Get library description."""
    return LIBRARY_INFO['description']


@register.simple_tag
def tailwind_lib_url():
    """Get library URL."""
    return LIBRARY_INFO['url']


@register.simple_tag
def tailwind_lib_author():
    """Get library author."""
    return LIBRARY_INFO['author']


@register.simple_tag
def tailwind_lib_info():
    """
    Get complete library info as dictionary.

    Usage in template:
        {% load tailwind_info %}
        {% tailwind_lib_info as lib %}
        <p>{{ lib.name }} v{{ lib.version }}</p>
    """
    return LIBRARY_INFO


@register.simple_tag
def tailwind_powered_by():
    """
    Generate "Powered by" HTML snippet.

    Usage:
        {% load tailwind_info %}
        {% tailwind_powered_by %}
    """
    return mark_safe(
        f'Powered by <a href="{LIBRARY_INFO["url"]}" '
        f'class="font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors" '
        f'target="_blank">{LIBRARY_INFO["name"]}</a> v{LIBRARY_INFO["version"]}'
    )


@register.simple_tag
def tailwind_footer_text():
    """
    Generate footer text with library info.

    Usage:
        {% load tailwind_info %}
        {% tailwind_footer_text %}
    """
    return mark_safe(
        f'<span class="text-gray-600 dark:text-gray-400">{LIBRARY_INFO["name"]}</span> '
        f'<span class="text-gray-400 dark:text-gray-600">v{LIBRARY_INFO["version"]}</span>'
    )


@register.filter
def add_class(field, css_class):
    """
    Add CSS class to form field.

    Usage:
        {{ form.field|add_class:"custom-class" }}
    """
    return field.as_widget(attrs={"class": css_class})


@register.simple_tag(takes_context=True)
def get_admin_url(context):
    """
    Get admin URL from settings or default.

    Usage:
        {% load tailwind_info %}
        {% get_admin_url as admin_url %}
        <a href="{{ admin_url }}">Admin</a>
    """
    from django.conf import settings
    from django.urls import reverse

    # Try to get custom admin URL from settings
    admin_url = getattr(settings, 'ADMIN_URL', None)

    if not admin_url:
        try:
            admin_url = reverse('admin:index')
        except Exception:
            admin_url = '/admin/'

    return admin_url


@register.simple_tag(takes_context=True)
def get_user_display_name(context):
    """
    Get user display name (full name or username).

    Usage:
        {% load tailwind_info %}
        {% get_user_display_name as user_name %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return 'Guest'

    user = request.user

    # Try full name first
    full_name = user.get_full_name() if hasattr(user, 'get_full_name') else ''
    if full_name:
        return full_name

    # Fallback to username
    return user.username if hasattr(user, 'username') else 'User'


@register.simple_tag(takes_context=True)
def get_user_initials(context):
    """
    Get user initials for avatar.

    Usage:
        {% load tailwind_info %}
        {% get_user_initials as initials %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return '?'

    user = request.user

    # Try to get initials from full name
    if hasattr(user, 'get_full_name'):
        full_name = user.get_full_name()
        if full_name:
            parts = full_name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}".upper()
            elif len(parts) == 1:
                return parts[0][:2].upper()

    # Fallback to username
    username = user.username if hasattr(user, 'username') else 'U'
    return username[:2].upper()
