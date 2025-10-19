"""
DRF ViewSets for IPC/RPC module.

Provides REST API endpoints with OpenAPI documentation using ViewSets and Routers.
"""

import logging

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..serializers import (
    HealthCheckSerializer,
    MethodStatsSerializer,
    NotificationStatsSerializer,
    OverviewStatsSerializer,
    RecentRequestsSerializer,
)
from ..services import RPCMonitor

logger = logging.getLogger(__name__)


class RPCMonitorViewSet(viewsets.ViewSet):
    """
    ViewSet for RPC monitoring and statistics.

    Provides comprehensive monitoring data for the RPC system.
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['IPC/RPC'],
        summary="Get RPC health status",
        description="Returns the current health status of the RPC monitoring system.",
        responses={
            200: HealthCheckSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=['get'], url_path='health')
    def health(self, request):
        """Get health status of RPC monitoring."""
        try:
            monitor = RPCMonitor()
            health_data = monitor.health_check()

            serializer = HealthCheckSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data)

        except ConnectionError as e:
            logger.error(f"Health check connection error: {e}")
            return Response(
                {"error": "Redis connection unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=['IPC/RPC'],
        summary="Get overview statistics",
        description="Returns overview statistics for RPC monitoring.",
        responses={
            200: OverviewStatsSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request):
        """Get overview statistics for RPC monitoring."""
        try:
            monitor = RPCMonitor()
            stats_data = monitor.get_overview_stats()

            serializer = OverviewStatsSerializer(data=stats_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data)

        except ValueError as e:
            logger.warning(f"Overview stats validation error: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ConnectionError as e:
            logger.error(f"Overview stats connection error: {e}")
            return Response(
                {"error": "Redis connection unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Overview stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=['IPC/RPC'],
        summary="Get recent RPC requests",
        description="Returns a list of recent RPC requests with their details.",
        parameters=[
            OpenApiParameter(
                name="count",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of requests to return (default: 50, max: 200)",
                required=False,
            ),
        ],
        responses={
            200: RecentRequestsSerializer,
            400: {"description": "Invalid parameters"},
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=['get'], url_path='requests')
    def requests(self, request):
        """Get recent RPC requests."""
        try:
            count = int(request.GET.get('count', 50))
            count = min(count, 200)  # Max 200

            monitor = RPCMonitor()
            requests_list = monitor.get_recent_requests(count=count)

            response_data = {
                'requests': requests_list,
                'count': len(requests_list),
                'total_available': monitor.get_total_requests_count()
            }

            serializer = RecentRequestsSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data)

        except ValueError as e:
            logger.warning(f"Recent requests validation error: {e}")
            return Response(
                {"error": "Invalid count parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ConnectionError as e:
            logger.error(f"Recent requests connection error: {e}")
            return Response(
                {"error": "Redis connection unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Recent requests error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=['IPC/RPC'],
        summary="Get notification statistics",
        description="Returns statistics about RPC notifications.",
        responses={
            200: NotificationStatsSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=['get'], url_path='notifications')
    def notifications(self, request):
        """Get notification statistics."""
        try:
            monitor = RPCMonitor()
            stats_data = monitor.get_notification_stats()

            serializer = NotificationStatsSerializer(data=stats_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data)

        except ConnectionError as e:
            logger.error(f"Notification stats connection error: {e}")
            return Response(
                {"error": "Redis connection unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Notification stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=['IPC/RPC'],
        summary="Get method statistics",
        description="Returns statistics grouped by RPC method.",
        responses={
            200: MethodStatsSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=['get'], url_path='methods')
    def methods(self, request):
        """Get statistics grouped by RPC method."""
        try:
            monitor = RPCMonitor()
            methods_list = monitor.get_method_stats()

            # Calculate total calls
            total_calls = sum(method.get('count', 0) for method in methods_list)

            response_data = {
                'methods': methods_list,
                'count': len(methods_list),
                'total_calls': total_calls
            }

            serializer = MethodStatsSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data)

        except ConnectionError as e:
            logger.error(f"Method stats connection error: {e}")
            return Response(
                {"error": "Redis connection unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Method stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
