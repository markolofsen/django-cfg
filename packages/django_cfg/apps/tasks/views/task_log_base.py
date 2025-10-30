"""
TaskLog Base ViewSet.

Base viewset with common configuration for task log endpoints.
"""
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from django_cfg.mixins import AdminAPIMixin
from ..models import TaskLog
from ..serializers import (
    TaskLogSerializer,
    TaskLogListSerializer,
    TaskLogDetailSerializer,
)
from ..filters import TaskLogFilter


class TaskLogBaseViewSet(AdminAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    Base ViewSet for TaskLog monitoring.

    Provides read-only access to task execution logs with filtering and searching.
    Extended by mixins for additional functionality (stats, timeline, overview).
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    queryset = TaskLog.objects.all().order_by('-enqueue_time')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskLogFilter
    search_fields = ['task_name', 'job_id', 'queue_name', 'error_message', 'worker_id']
    ordering_fields = ['enqueue_time', 'start_time', 'finish_time', 'duration_ms', 'job_retries', 'created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TaskLogListSerializer
        elif self.action == 'retrieve':
            return TaskLogDetailSerializer
        return TaskLogSerializer
