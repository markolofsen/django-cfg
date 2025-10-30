"""
System ViewSet

Endpoints for system monitoring:
- GET /system/health/ - System health status
- GET /system/metrics/ - System performance metrics
"""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import SystemHealthService, StatisticsService
from ..serializers import SystemHealthSerializer, SystemMetricsSerializer

logger = logging.getLogger(__name__)


class SystemViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    System Monitoring ViewSet

    Provides endpoints for system health and performance metrics.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = SystemHealthSerializer

    @extend_schema(
        summary="Get system health status",
        description="Retrieve overall system health including all component checks",
        responses={200: SystemHealthSerializer},
        tags=["Dashboard - System"]
    )
    @action(detail=False, methods=['get'], url_path='health', serializer_class=SystemHealthSerializer)
    def health(self, request):
        """Get overall system health status."""
        try:
            health_service = SystemHealthService()
            health_data = health_service.get_overall_health_status()
            return Response(health_data)

        except Exception as e:
            logger.error(f"System health API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get system metrics",
        description="Retrieve system performance metrics (CPU, memory, disk, etc.)",
        responses={200: SystemMetricsSerializer},
        tags=["Dashboard - System"]
    )
    @action(detail=False, methods=['get'], url_path='metrics', serializer_class=SystemMetricsSerializer)
    def metrics(self, request):
        """Get system performance metrics."""
        try:
            stats_service = StatisticsService()
            metrics = stats_service.get_system_metrics()
            return Response(metrics)

        except Exception as e:
            logger.error(f"System metrics API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
