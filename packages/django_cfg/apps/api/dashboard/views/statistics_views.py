"""
Statistics ViewSet

Endpoints for dashboard statistics:
- GET /statistics/cards/ - Statistics cards
- GET /statistics/users/ - User statistics
- GET /statistics/apps/ - Application statistics
"""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import StatisticsService
from ..serializers import (
    StatCardSerializer,
    UserStatisticsSerializer,
    AppStatisticsSerializer,
)

logger = logging.getLogger(__name__)


class StatisticsViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    Statistics ViewSet

    Provides endpoints for retrieving various dashboard statistics.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = StatCardSerializer

    @extend_schema(
        summary="Get statistics cards",
        description="Retrieve dashboard statistics cards with key metrics",
        responses=StatCardSerializer(many=True),
        tags=["Dashboard - Statistics"]
    )
    @action(detail=False, methods=['get'], url_path='cards', pagination_class=None, serializer_class=StatCardSerializer)
    def cards(self, request):
        """Get dashboard statistics cards."""
        try:
            stats_service = StatisticsService()
            cards = stats_service.get_stat_cards()
            return Response(cards)

        except Exception as e:
            logger.error(f"Stat cards API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get user statistics",
        description="Retrieve user-related statistics",
        responses={200: UserStatisticsSerializer},
        tags=["Dashboard - Statistics"]
    )
    @action(detail=False, methods=['get'], url_path='users', serializer_class=UserStatisticsSerializer)
    def users(self, request):
        """Get user statistics."""
        try:
            stats_service = StatisticsService()
            user_stats = stats_service.get_user_statistics()
            return Response(user_stats)

        except Exception as e:
            logger.error(f"User statistics API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get application statistics",
        description="Retrieve statistics for all enabled django-cfg applications",
        responses=AppStatisticsSerializer(many=True),
        tags=["Dashboard - Statistics"]
    )
    @action(detail=False, methods=['get'], url_path='apps', pagination_class=None, serializer_class=AppStatisticsSerializer)
    def apps(self, request):
        """Get application-specific statistics."""
        try:
            stats_service = StatisticsService()
            app_stats = stats_service.get_app_statistics()

            # Convert dict to list of {app_name, statistics} objects
            # Only iterate over the 'apps' key, not the aggregated totals
            data = [
                {'app_name': app_name, 'statistics': stats}
                for app_name, stats in app_stats.get('apps', {}).items()
            ]

            return Response(data)

        except Exception as e:
            logger.error(f"App statistics API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
