"""
TaskLog Overview Actions.

Provides high-level summary statistics for the entire task system.
"""
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import TaskLog
from ..serializers import TaskLogOverviewSerializer


class TaskLogOverviewMixin:
    """
    Mixin for task system overview endpoints.

    Provides high-level statistics:
    - Total task counts
    - Active queues
    - Recent failures
    - Distribution by queue and status
    """

    @extend_schema(
        responses={200: TaskLogOverviewSerializer},
        summary="Task System Overview",
        description="Get high-level summary statistics for the entire task system"
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get summary overview of task system.

        Returns properly structured data validated by TaskLogOverviewSerializer.

        Returns:
            {
                "total_tasks": 1500,
                "active_queues": ["default", "high", "knowledge"],
                "recent_failures": 5,
                "tasks_by_queue": [
                    {"queue_name": "default", "count": 800},
                    {"queue_name": "high", "count": 500},
                    {"queue_name": "knowledge", "count": 200}
                ],
                "tasks_by_status": [
                    {"status": "success", "count": 1450},
                    {"status": "failed", "count": 45},
                    {"status": "in_progress", "count": 5}
                ]
            }
        """
        # Get all-time statistics
        total_tasks = TaskLog.objects.count()

        # Get active queues
        active_queues = list(
            TaskLog.objects.values_list('queue_name', flat=True)
            .distinct()
            .order_by('queue_name')
        )

        # Recent failures (last 24 hours)
        time_threshold = timezone.now() - timedelta(hours=24)
        recent_failures = TaskLog.objects.filter(
            Q(success=False) | Q(status__in=['failed', 'expired']),
            created_at__gte=time_threshold
        ).count()

        # Tasks by queue - convert to array of objects
        tasks_by_queue = [
            {'queue_name': item['queue_name'], 'count': item['count']}
            for item in TaskLog.objects.values('queue_name')
            .annotate(count=Count('id'))
            .order_by('queue_name')
        ]

        # Tasks by status - convert to array of objects
        tasks_by_status = [
            {'status': item['status'], 'count': item['count']}
            for item in TaskLog.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        ]

        overview_data = {
            'total_tasks': total_tasks,
            'active_queues': active_queues,
            'recent_failures': recent_failures,
            'tasks_by_queue': tasks_by_queue,
            'tasks_by_status': tasks_by_status,
        }

        # Validate and serialize data
        serializer = TaskLogOverviewSerializer(overview_data)
        return Response(serializer.data)
