"""
Django DRF Theme templatetags.

Custom template tags and filters for DRF Tailwind theme.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def tailwind_css():
    """Load Tailwind CSS from CDN with dark mode configuration."""
    return mark_safe('''
        <script src="https://cdn.tailwindcss.com?plugins=forms,typography,aspect-ratio,container-queries"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {}
                }
            }
        </script>
    ''')


@register.filter
def add_class(field, css_class):
    """Add CSS class to form field."""
    return field.as_widget(attrs={"class": css_class})


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.simple_tag
def get_theme_class(theme='auto'):
    """Get theme class for HTML element."""
    if theme == 'dark':
        return 'dark'
    elif theme == 'light':
        return ''
    else:  # auto
        return ''  # System preference will be handled by CSS


@register.filter
def prettify_json(value):
    """Prettify JSON for display."""
    import json
    try:
        if isinstance(value, str):
            obj = json.loads(value)
        else:
            obj = value
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except (ValueError, TypeError):
        return value
