"""
Overview ViewSet

Endpoint for complete dashboard overview:
- GET /overview/ - Complete dashboard data in single request
"""

import logging
from datetime import datetime

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from django_cfg.extensions.loader import get_extension_loader
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

    @transaction.non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        """Disable atomic requests for this viewset."""
        return super().dispatch(request, *args, **kwargs)

    @extend_schema(
        summary="Get dashboard overview",
        description="Retrieve complete dashboard data including stats, health, actions, and metrics",
        responses={200: DashboardOverviewSerializer},
        tags=["Dashboard - Overview"]
    )
    @action(detail=False, methods=['get'], url_path='', url_name='overview')
    def overview(self, request):
        """Get complete dashboard overview."""
        try:
            stats_service = StatisticsService()
            health_service = SystemHealthService()
            charts_service = ChartsService()

            # Get app statistics - wrapped in try/except since it queries all models
            try:
                app_stats_dict = stats_service.get_app_statistics()
            except Exception as e:
                logger.error(f"Error getting app stats: {e}")
                app_stats_dict = {'apps': {}}

            app_statistics_list = [
                {
                    'app_name': app_label,
                    'statistics': {
                        'name': app_data.get('name', ''),
                        'models': app_data.get('models', []),
                        'total_records': app_data.get('total_records', 0),
                        'model_count': app_data.get('model_count', 0),
                    }
                }
                for app_label, app_data in app_stats_dict.get('apps', {}).items()
            ]

            # Get installed extensions
            try:
                extension_loader = get_extension_loader()
                extensions_info = extension_loader.get_extension_info()
                # Filter to only valid app extensions
                extensions = [
                    {
                        'name': ext['name'],
                        'type': ext['type'],
                        'version': ext['version'],
                        'is_valid': ext['is_valid'],
                        'description': ext['description'],
                    }
                    for ext in extensions_info
                    if ext['type'] == 'app' and ext['is_valid']
                ]
            except Exception as e:
                logger.warning(f"Failed to get extensions info: {e}")
                extensions = []

            data = {
                # Statistics
                'stat_cards': stats_service.get_stat_cards(),
                'user_statistics': stats_service.get_user_statistics(),
                'app_statistics': app_statistics_list,

                # System
                'system_health': health_service.get_overall_health_status(),
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

                # Extensions
                'extensions': extensions,

                # Meta
                'timestamp': datetime.now().isoformat(),
            }

            return Response(data)

        except Exception as e:
            logger.error(f"Dashboard overview API error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
