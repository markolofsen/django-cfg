"""
Dashboard views for Django CFG Tasks app.

Provides template-based dashboard views for task monitoring.
"""

import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

logger = logging.getLogger(__name__)


@staff_member_required
def dashboard_view(request):
    """
    Main dashboard view for task monitoring.
    
    Provides a comprehensive overview of:
    - Queue status and statistics
    - Worker information
    - Task execution metrics
    - Recent task history
    """
    try:
        # Use simulator to get data
        from ..utils.simulator import TaskSimulator
        simulator = TaskSimulator()

        # Build navigation items for navbar
        tasks_nav_items = [
            {
                'label': 'Task History',
                'url': '/admin/django_dramatiq/task/',
                'icon': '📜',
            },
            {
                'label': 'Settings',
                'url': '/admin/constance/config/',
                'icon': '⚙️',
            },
        ]

        # Prepare context data
        context = {
            'queue_status': simulator.get_current_queue_status(),
            'task_stats': simulator.get_current_task_statistics(),
            'tasks_nav_items': tasks_nav_items,
        }

        return render(request, 'tasks/pages/dashboard.html', context)

    except Exception as e:
        logger.error(f"Dashboard view error: {e}")

        # Build navigation items for navbar
        tasks_nav_items = [
            {
                'label': 'Task History',
                'url': '/admin/django_dramatiq/task/',
                'icon': '📜',
            },
            {
                'label': 'Settings',
                'url': '/admin/constance/config/',
                'icon': '⚙️',
            },
        ]

        # Provide fallback context for error cases
        context = {
            'queue_status': {
                'error': str(e),
                'queues': {},
                'workers': 0,
                'redis_connected': False,
                'timestamp': None
            },
            'task_stats': {
                'error': str(e),
                'statistics': {'total': 0},
                'recent_tasks': [],
                'timestamp': None
            },
            'tasks_nav_items': tasks_nav_items,
        }

        return render(request, 'tasks/pages/dashboard.html', context)
