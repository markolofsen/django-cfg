"""
Activity ViewSet

Endpoints for activity tracking:
- GET /activity/recent/ - Recent activity entries
- GET /activity/actions/ - Quick action buttons
"""

import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.mixins import AdminAPIMixin
from ..services import StatisticsService, SystemHealthService
from ..serializers import ActivityEntrySerializer, QuickActionSerializer

logger = logging.getLogger(__name__)


class ActivityViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    Activity Tracking ViewSet

    Provides endpoints for recent activity and quick actions.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = ActivityEntrySerializer

    @extend_schema(
        summary="Get recent activity",
        description="Retrieve recent system activity entries",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Maximum number of entries to return',
                required=False,
                type=int,
                default=10
            ),
        ],
        responses=ActivityEntrySerializer(many=True),
        tags=["Dashboard - Activity"]
    )
    @action(detail=False, methods=['get'], url_path='recent', pagination_class=None, serializer_class=ActivityEntrySerializer)
    def recent(self, request):
        """Get recent activity entries."""
        try:
            limit = int(request.query_params.get('limit', 10))
            stats_service = StatisticsService()
            activity = stats_service.get_recent_activity(limit=limit)
            return Response(activity)

        except Exception as e:
            logger.error(f"Recent activity API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get quick actions",
        description="Retrieve quick action buttons for dashboard",
        responses=QuickActionSerializer(many=True),
        tags=["Dashboard - Activity"]
    )
    @action(detail=False, methods=['get'], url_path='actions', pagination_class=None, serializer_class=QuickActionSerializer)
    def actions(self, request):
        """Get quick action buttons."""
        try:
            health_service = SystemHealthService()
            actions = health_service.get_quick_actions()
            return Response(actions)

        except Exception as e:
            logger.error(f"Quick actions API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
