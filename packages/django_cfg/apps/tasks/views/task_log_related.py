"""
TaskLog Related Tasks Actions.

Provides endpoints for finding related task executions.
"""
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import TaskLog
from ..serializers import TaskLogListSerializer


class TaskLogRelatedMixin:
    """
    Mixin for related tasks endpoints.

    Provides functionality to find related task executions:
    - Same job_id (retries)
    - Same task_name (similar executions)
    """

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """
        Get related task logs (same job_id or task_name).

        Returns tasks that share the same job_id or are retries of the same task.

        Returns:
            Array of related TaskLog objects (up to 10 most recent)
        """
        task_log = self.get_object()

        # Find related tasks
        related = TaskLog.objects.filter(
            Q(job_id=task_log.job_id) | Q(task_name=task_log.task_name)
        ).exclude(id=task_log.id).order_by('-created_at')[:10]

        serializer = TaskLogListSerializer(related, many=True)
        return Response(serializer.data)
