"""
Charts ViewSet

Endpoints for dashboard charts and analytics:
- GET /charts/registrations/ - User registration chart
- GET /charts/activity/ - User activity chart
- GET /charts/tracker/ - Activity tracker (52 weeks)
- GET /charts/recent-users/ - Recent users list
"""

import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import ChartsService, StatisticsService
from ..serializers import (
    ChartDataSerializer,
    ActivityTrackerDaySerializer,
    RecentUserSerializer,
)

logger = logging.getLogger(__name__)


class ChartsViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    Charts ViewSet

    Provides endpoints for dashboard charts and analytics.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = ChartDataSerializer

    @extend_schema(
        summary="Get user registration chart",
        description="Retrieve user registration data for chart visualization",
        parameters=[
            OpenApiParameter(
                name='days',
                description='Number of days to include',
                required=False,
                type=int,
                default=7
            ),
        ],
        responses={200: ChartDataSerializer},
        tags=["Dashboard - Charts"]
    )
    @action(detail=False, methods=['get'], url_path='registrations', serializer_class=ChartDataSerializer)
    def registrations(self, request):
        """Get user registration chart data."""
        try:
            days = int(request.query_params.get('days', 7))
            charts_service = ChartsService()
            chart_data = charts_service.get_user_registration_chart(days=days)
            return Response(chart_data)

        except Exception as e:
            logger.error(f"Registration chart API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get user activity chart",
        description="Retrieve user activity data for chart visualization",
        parameters=[
            OpenApiParameter(
                name='days',
                description='Number of days to include',
                required=False,
                type=int,
                default=7
            ),
        ],
        responses={200: ChartDataSerializer},
        tags=["Dashboard - Charts"]
    )
    @action(detail=False, methods=['get'], url_path='activity', serializer_class=ChartDataSerializer)
    def activity(self, request):
        """Get user activity chart data."""
        try:
            days = int(request.query_params.get('days', 7))
            charts_service = ChartsService()
            chart_data = charts_service.get_user_activity_chart(days=days)
            return Response(chart_data)

        except Exception as e:
            logger.error(f"Activity chart API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get activity tracker",
        description="Retrieve activity tracker data (GitHub-style contribution graph)",
        parameters=[
            OpenApiParameter(
                name='weeks',
                description='Number of weeks to include',
                required=False,
                type=int,
                default=52
            ),
        ],
        responses=ActivityTrackerDaySerializer(many=True),
        tags=["Dashboard - Charts"]
    )
    @action(detail=False, methods=['get'], url_path='tracker', pagination_class=None, serializer_class=ActivityTrackerDaySerializer)
    def tracker(self, request):
        """Get activity tracker data."""
        try:
            weeks = int(request.query_params.get('weeks', 52))
            charts_service = ChartsService()
            tracker_data = charts_service.get_activity_tracker(weeks=weeks)
            return Response(tracker_data)

        except Exception as e:
            logger.error(f"Activity tracker API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get recent users",
        description="Retrieve list of recently registered users",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Maximum number of users to return',
                required=False,
                type=int,
                default=10
            ),
        ],
        responses=RecentUserSerializer(many=True),
        tags=["Dashboard - Charts"]
    )
    @action(detail=False, methods=['get'], url_path='recent-users', pagination_class=None, serializer_class=RecentUserSerializer)
    def recent_users(self, request):
        """Get recent users list."""
        try:
            limit = int(request.query_params.get('limit', 10))
            stats_service = StatisticsService()
            users = stats_service.get_recent_users(limit=limit)
            return Response(users)

        except Exception as e:
            logger.error(f"Recent users API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
