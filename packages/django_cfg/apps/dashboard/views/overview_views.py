"""
Overview ViewSet

Endpoint for complete dashboard overview:
- GET /overview/ - Complete dashboard data in single request
"""

import logging
from datetime import datetime

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import StatisticsService, SystemHealthService, ChartsService
from ..serializers import DashboardOverviewSerializer

logger = logging.getLogger(__name__)


class OverviewViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    Dashboard Overview ViewSet

    Provides a single endpoint that returns all dashboard data at once.
    Useful for initial page load.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = DashboardOverviewSerializer

    @extend_schema(
        summary="Get dashboard overview",
        description="Retrieve complete dashboard data including stats, health, actions, and metrics",
        responses={200: DashboardOverviewSerializer},
        tags=["Dashboard - Overview"]
    )
    @action(detail=False, methods=['get'], url_path='', url_name='overview')
    def overview(self, request):
        """
        Get complete dashboard overview.

        Returns all dashboard data in a single request:
        - Statistics cards
        - System health status
        - Quick actions
        - Recent activity
        - System metrics
        - User statistics
        """
        try:
            stats_service = StatisticsService()
            health_service = SystemHealthService()
            charts_service = ChartsService()

            data = {
                # Statistics
                'stat_cards': stats_service.get_stat_cards(),
                'user_statistics': stats_service.get_user_statistics(),
                'app_statistics': stats_service.get_app_statistics(),

                # System
                'system_health': health_service.get_all_health_checks(),
                'system_metrics': stats_service.get_system_metrics(),

                # Activity
                'recent_activity': stats_service.get_recent_activity(limit=10),
                'recent_users': stats_service.get_recent_users(limit=10),
                'quick_actions': health_service.get_quick_actions(),

                # Charts
                'charts': {
                    'user_registrations': charts_service.get_user_registration_chart(days=7),
                    'user_activity': charts_service.get_user_activity_chart(days=7),
                },
                'activity_tracker': charts_service.get_activity_tracker(weeks=52),

                # Meta
                'timestamp': datetime.now().isoformat(),
            }

            return Response(data)

        except Exception as e:
            logger.error(f"Dashboard overview API error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
