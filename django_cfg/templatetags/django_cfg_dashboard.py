"""
Template tags: custom admin dashboard tabs.
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_dashboard_config(context):
    """
    Return DashboardConfig for the current staff user, or None if not configured.

    Usage:
        {% load django_cfg_dashboard %}
        {% get_dashboard_config as dashboard %}
        {% if dashboard %}
            {% include "django_dashboard/tabs_bar.html" with all_tabs=dashboard.tabs current_tab=dashboard.tabs.0 dashboard_config=dashboard %}
        {% endif %}
    """
    try:
        request = context.get('request')
        if not request or not getattr(request.user, 'is_staff', False):
            return None

        # The merge lives in ONE place — see modules/django_dashboard/resolver.py.
        # It used to be duplicated here, and the copy in views/tab.py disagreed,
        # so extension tabs rendered in this bar and then 404'd when clicked.
        from django_cfg.modules.django_dashboard.resolver import get_dashboard_config

        return get_dashboard_config()
    except Exception:
        return None
