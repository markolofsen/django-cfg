"""
Dashboard view for IPC/RPC monitoring.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def dashboard_view(request):
    """Render the IPC/RPC dashboard template."""
    context = {
        'page_title': 'IPC/RPC Monitor Dashboard',
    }
    return render(request, 'django_cfg_ipc/dashboard.html', context)
