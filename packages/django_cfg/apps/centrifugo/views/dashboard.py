"""
Dashboard view for Centrifugo monitoring.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse


@staff_member_required
def dashboard_view(request):
    """Render the Centrifugo dashboard template."""

    # Navigation items for the navbar
    nav_items = [
        {
            'label': 'Logs',
            'url': reverse('admin:django_cfg_centrifugo_centrifugolog_changelist'),
            'icon': 'list_alt',
            'active': False,
        },
    ]

    context = {
        'page_title': 'Centrifugo Monitor Dashboard',
        'centrifugo_nav_items': nav_items,
    }
    return render(request, 'django_cfg_centrifugo/pages/dashboard.html', context)
