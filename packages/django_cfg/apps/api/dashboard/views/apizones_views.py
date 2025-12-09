"""
API Zones ViewSet

Endpoints for OpenAPI zones/groups management:
- GET /zones/ - All API zones
- GET /zones/summary/ - Zones summary with statistics
"""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import APIZonesService
from ..serializers import APIZoneSerializer, APIZonesSummarySerializer

logger = logging.getLogger(__name__)


class APIZonesViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    API Zones ViewSet

    Provides endpoints for OpenAPI zones (groups) management.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = APIZoneSerializer
    pagination_class = None  # Disable pagination for zones list

    @extend_schema(
        summary="Get all API zones",
        description="Retrieve all OpenAPI zones/groups with their configuration",
        responses={200: APIZoneSerializer(many=True)},
        tags=["Dashboard - API Zones"]
    )
    def list(self, request):
        """Get all API zones."""
        try:
            zones_service = APIZonesService()
            zones_list, _ = zones_service.get_zones_data()
            return Response(zones_list)

        except Exception as e:
            logger.error(f"API zones list error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get zones summary",
        description="Retrieve zones summary with statistics",
        responses={200: APIZonesSummarySerializer},
        tags=["Dashboard - API Zones"]
    )
    @action(detail=False, methods=['get'], url_path='summary', serializer_class=APIZonesSummarySerializer)
    def summary(self, request):
        """Get zones summary with statistics."""
        try:
            zones_service = APIZonesService()
            summary = zones_service.get_zones_summary()
            return Response(summary)

        except Exception as e:
            logger.error(f"API zones summary error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
