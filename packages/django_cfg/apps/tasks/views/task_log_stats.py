"""
TaskLog Statistics Actions.

Provides aggregated statistics and metrics for task execution monitoring.
"""
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import TaskLog
from ..serializers import TaskLogStatsSerializer


class TaskLogStatsMixin:
    """
    Mixin for task statistics endpoints.

    Provides aggregated statistics about task execution:
    - Success/failure rates
    - Average durations
    - Task counts by status
    """

    @extend_schema(
        responses={200: TaskLogStatsSerializer},
        summary="Task Execution Statistics",
        description="Get aggregated statistics about task execution (success/failure rates, duration)"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get aggregated task statistics.

        Query Parameters:
            period_hours (int): Statistics period in hours (default: 24)
            task_name (str): Filter by specific task name

        Returns:
            {
                "total": 150,
                "successful": 145,
                "failed": 5,
                "in_progress": 2,
                "success_rate": 96.67,
                "avg_duration_ms": 1250,
                "avg_duration_seconds": 1.25,
                "period_hours": 24
            }
        """
        period_hours = int(request.query_params.get('period_hours', 24))
        task_name = request.query_params.get('task_name')

        # Calculate time threshold
        time_threshold = timezone.now() - timedelta(hours=period_hours)

        # Base queryset
        queryset = TaskLog.objects.filter(created_at__gte=time_threshold)
        if task_name:
            queryset = queryset.filter(task_name=task_name)

        # Calculate statistics
        total = queryset.count()
        successful = queryset.filter(success=True).count()
        failed = queryset.filter(success=False, status='failed').count()
        in_progress = queryset.filter(Q(status='in_progress') | Q(status='queued')).count()

        # Calculate success rate
        completed = successful + failed
        success_rate = (successful / completed * 100) if completed > 0 else 0.0

        # Calculate average duration (only for completed tasks)
        avg_duration = queryset.filter(
            duration_ms__isnull=False
        ).aggregate(avg=Avg('duration_ms'))['avg'] or 0

        stats_data = {
            'total': total,
            'successful': successful,
            'failed': failed,
            'in_progress': in_progress,
            'success_rate': round(success_rate, 2),
            'avg_duration_ms': int(avg_duration),
            'avg_duration_seconds': round(avg_duration / 1000, 2),
            'period_hours': period_hours,
        }

        serializer = TaskLogStatsSerializer(stats_data)
        return Response(serializer.data)
