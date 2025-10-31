"""
Django-Q2 ViewSet

API endpoints for Django-Q2 task monitoring.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..services.django_q2_service import DjangoQ2Service
from ..serializers.django_q2 import (
    DjangoQ2ScheduleSerializer,
    DjangoQ2TaskSerializer,
    DjangoQ2StatusSerializer,
    DjangoQ2SummarySerializer,
)


class DjangoQ2ViewSet(viewsets.ViewSet):
    """
    ViewSet for Django-Q2 task monitoring.

    Provides endpoints for:
    - Scheduled tasks list
    - Recent task executions
    - Cluster status
    - Complete summary
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def schedules(self, request):
        """
        Get all scheduled tasks.

        GET /api/django_q2/schedules/
        """
        schedules = DjangoQ2Service.get_schedules()
        serializer = DjangoQ2ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tasks(self, request):
        """
        Get recent task executions.

        GET /api/django_q2/tasks/
        Query params:
            - limit: Number of tasks to return (default: 20)
        """
        limit = int(request.query_params.get('limit', 20))
        tasks = DjangoQ2Service.get_recent_tasks(limit=limit)
        serializer = DjangoQ2TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get Django-Q2 cluster status.

        GET /api/django_q2/status/
        """
        status_data = DjangoQ2Service.get_cluster_status()
        serializer = DjangoQ2StatusSerializer(status_data)
        return Response(serializer.data)

    def list(self, request):
        """
        Get complete Django-Q2 summary.

        GET /api/django_q2/
        Returns status, schedules, and recent tasks.
        """
        summary = DjangoQ2Service.get_summary()
        serializer = DjangoQ2SummarySerializer(summary)
        return Response(serializer.data)
