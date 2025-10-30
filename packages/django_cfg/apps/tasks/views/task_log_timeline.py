"""
TaskLog Timeline Actions.

Provides time-series data for task execution visualization.
"""
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import TaskLog
from ..serializers import TaskLogTimelineSerializer


class TaskLogTimelineMixin:
    """
    Mixin for task timeline endpoints.

    Provides time-bucketed statistics for visualization:
    - Hourly/daily task counts
    - Success/failure trends
    - Performance metrics over time
    """

    @extend_schema(
        responses={200: TaskLogTimelineSerializer},
        summary="Task Execution Timeline",
        description="Get time-series data of task executions grouped by time intervals"
    )
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """
        Get task execution timeline grouped by time intervals.

        Returns timeline data wrapped in object with period/interval metadata.

        Query Parameters:
            period_hours (int): Timeline period in hours (default: 24)
            interval (str): Grouping interval - 'hour', 'day' (default: 'hour')
            task_name (str): Filter by specific task name

        Returns:
            {
                "period_hours": 24,
                "interval": "hour",
                "data": [
                    {
                        "timestamp": "2025-10-30T10:00:00Z",
                        "total": 15,
                        "successful": 14,
                        "failed": 1,
                        "avg_duration_ms": 1200
                    },
                    ...
                ]
            }
        """
        period_hours = int(request.query_params.get('period_hours', 24))
        interval = request.query_params.get('interval', 'hour')
        task_name = request.query_params.get('task_name')

        # Calculate time threshold
        time_threshold = timezone.now() - timedelta(hours=period_hours)

        # Base queryset
        queryset = TaskLog.objects.filter(created_at__gte=time_threshold)
        if task_name:
            queryset = queryset.filter(task_name=task_name)

        # TODO: Implement proper time-series grouping with SQL time bucketing
        # For now, return empty data array with correct structure
        timeline_data = {
            'period_hours': period_hours,
            'interval': interval,
            'data': []  # Empty for now - will be implemented later
        }

        # Validate and serialize
        serializer = TaskLogTimelineSerializer(timeline_data)
        return Response(serializer.data)
