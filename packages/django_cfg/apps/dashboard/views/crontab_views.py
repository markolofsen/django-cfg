"""
Crontab ViewSet

Endpoints for cron job monitoring:
- GET /crontab/jobs/ - List all configured cron jobs
- GET /crontab/status/ - Crontab configuration status
"""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import CrontabService
from ..serializers import CrontabJobsSerializer, CrontabStatusSerializer

logger = logging.getLogger(__name__)


class CrontabViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    Crontab Monitoring ViewSet

    Provides endpoints for monitoring scheduled cron jobs.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = CrontabJobsSerializer

    @extend_schema(
        summary="Get all cron jobs",
        description="Retrieve list of all configured cron jobs with schedules and details",
        responses={200: CrontabJobsSerializer},
        tags=["Dashboard - Crontab"]
    )
    @action(detail=False, methods=['get'], url_path='jobs', serializer_class=CrontabJobsSerializer)
    def jobs(self, request):
        """Get all configured cron jobs."""
        try:
            crontab_service = CrontabService()
            jobs_data = crontab_service.get_all_jobs()
            return Response(jobs_data)

        except Exception as e:
            logger.error(f"Crontab jobs API error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get crontab status",
        description="Retrieve crontab configuration status and summary",
        responses={200: CrontabStatusSerializer},
        tags=["Dashboard - Crontab"]
    )
    @action(detail=False, methods=['get'], url_path='status', serializer_class=CrontabStatusSerializer)
    def crontab_status(self, request):
        """Get crontab configuration status."""
        try:
            crontab_service = CrontabService()
            status_data = crontab_service.get_status()
            return Response(status_data)

        except Exception as e:
            logger.error(f"Crontab status API error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
