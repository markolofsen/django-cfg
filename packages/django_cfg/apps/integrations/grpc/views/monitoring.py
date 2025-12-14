"""
gRPC Monitoring ViewSet.

Provides REST API endpoints for monitoring gRPC request statistics.
"""

from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Avg, Count, Max
from django.db.models.functions import TruncDay, TruncHour
from django_cfg.mixins import AdminAPIMixin
from django_cfg.middleware.pagination import DefaultPagination
from django_cfg.utils import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import GRPCRequestLog
from ..serializers import (
    GRPCHealthCheckSerializer,
    GRPCOverviewStatsSerializer,
    MethodListSerializer,
    MethodStatsSerializer,
)
from ..serializers.service_registry import RecentRequestSerializer
from ..services import MonitoringService

logger = get_logger("grpc.monitoring")


class GRPCMonitorViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    ViewSet for gRPC monitoring and statistics.

    Provides comprehensive monitoring data for gRPC requests including:
    - Health checks
    - Overview statistics
    - Recent requests
    - Service-level statistics
    - Method-level statistics
    - Timeline data

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    pagination_class = DefaultPagination

    # Required for GenericViewSet
    queryset = GRPCRequestLog.objects.none()  # Placeholder, actual queries in actions
    serializer_class = RecentRequestSerializer  # Default serializer for schema

    @extend_schema(
        tags=["gRPC Monitoring"],
        summary="Get gRPC health status",
        description="Returns the current health status of the gRPC server.",
        responses={
            200: GRPCHealthCheckSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=["get"], url_path="health")
    def health(self, request):
        """Get health status of gRPC server."""
        try:
            service = MonitoringService()
            health_data = service.get_health_status()
            serializer = GRPCHealthCheckSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Monitoring"],
        summary="Get overview statistics",
        description="Returns overview statistics for gRPC requests.",
        parameters=[
            OpenApiParameter(
                name="hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Statistics period in hours (default: 24)",
                required=False,
            ),
        ],
        responses={
            200: GRPCOverviewStatsSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="overview")
    def overview(self, request):
        """Get overview statistics for gRPC requests."""
        try:
            hours = int(request.GET.get("hours", 24))

            service = MonitoringService()
            stats = service.get_overview_statistics(hours=hours)
            serializer = GRPCOverviewStatsSerializer(data=stats)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except ValueError as e:
            logger.warning(f"Overview stats validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Overview stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Monitoring"],
        summary="Get recent requests",
        description="Returns a list of recent gRPC requests with their details. Uses standard DRF pagination.",
        parameters=[
            OpenApiParameter(
                name="service",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by service name",
                required=False,
            ),
            OpenApiParameter(
                name="method",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by method name",
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by status (success, error, timeout, pending, cancelled)",
                required=False,
            ),
        ],
        responses={
            200: RecentRequestSerializer(many=True),  # Use many=True for paginated list
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="requests")
    def requests(self, request):
        """Get recent gRPC requests."""
        try:
            service_filter = request.GET.get("service")
            method_filter = request.GET.get("method")
            status_filter = request.GET.get("status")

            service = MonitoringService()
            queryset = service.get_recent_requests(
                service_name=service_filter,
                method_name=method_filter,
                status_filter=status_filter,
            )

            # Use DRF pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                # Serialize paginated data
                requests_list = []
                for req in page:
                    requests_list.append({
                        "id": req.id,
                        "request_id": req.request_id,
                        "service_name": req.service_name,
                        "method_name": req.method_name,
                        "status": req.status,
                        "duration_ms": req.duration_ms or 0,
                        "grpc_status_code": req.grpc_status_code or "",
                        "error_message": req.error_message or "",
                        "created_at": req.created_at.isoformat(),
                        "client_ip": req.client_ip or "",
                        # User information
                        "user_id": req.user.id if req.user else None,
                        "username": req.user.username if req.user else "",
                        "is_authenticated": req.is_authenticated,
                        # API Key information
                        "api_key_id": req.api_key.id if req.api_key else None,
                        "api_key_name": req.api_key.name if req.api_key else "",
                    })
                return self.get_paginated_response(requests_list)

            # No pagination fallback
            requests_list = []
            for req in queryset[:100]:
                requests_list.append({
                    "id": req.id,
                    "request_id": req.request_id,
                    "service_name": req.service_name,
                    "method_name": req.method_name,
                    "status": req.status,
                    "duration_ms": req.duration_ms or 0,
                    "grpc_status_code": req.grpc_status_code or "",
                    "error_message": req.error_message or "",
                    "created_at": req.created_at.isoformat(),
                    "client_ip": req.client_ip or "",
                    # User information
                    "user_id": req.user.id if req.user else None,
                    "username": req.user.username if req.user else "",
                    "is_authenticated": req.is_authenticated,
                    # API Key information
                    "api_key_id": req.api_key.id if req.api_key else None,
                    "api_key_name": req.api_key.name if req.api_key else "",
                })
            return Response({"requests": requests_list, "count": len(requests_list)})

        except ValueError as e:
            logger.warning(f"Recent requests validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Recent requests error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Monitoring"],
        summary="Get method statistics",
        description="Returns statistics grouped by method.",
        parameters=[
            OpenApiParameter(
                name="hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Statistics period in hours (default: 24)",
                required=False,
            ),
            OpenApiParameter(
                name="service",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by service name",
                required=False,
            ),
        ],
        responses={
            200: MethodListSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="methods", pagination_class=None)
    def methods(self, request):
        """Get statistics per method."""
        try:
            hours = int(request.GET.get("hours", 24))
            service_filter = request.GET.get("service")

            service = MonitoringService()
            methods_list = service.get_method_statistics(
                service_name=service_filter,
                hours=hours
            )

            response_data = {
                "methods": methods_list,
                "total_methods": len(methods_list),
            }

            serializer = MethodListSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except ValueError as e:
            logger.warning(f"Method stats validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Method stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Monitoring"],
        summary="Get request timeline",
        description="Returns hourly or daily breakdown of request counts for charts.",
        parameters=[
            OpenApiParameter(
                name="hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Time period in hours (default: 24)",
                required=False,
            ),
            OpenApiParameter(
                name="interval",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Time interval: 'hour' or 'day' (default: hour)",
                required=False,
            ),
        ],
        responses={
            200: {"description": "Timeline data"},
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="timeline")
    def timeline(self, request):
        """Get request timeline breakdown for charts."""
        try:
            hours = int(request.GET.get("hours", 24))
            interval = request.GET.get("interval", "hour")

            if interval not in ["hour", "day"]:
                interval = "hour"

            service = MonitoringService()
            timeline_list = service.get_timeline_data(
                hours=hours,
                granularity=interval
            )

            response_data = {
                "timeline": timeline_list,
                "period_hours": hours,
                "interval": interval,
            }

            return Response(response_data)

        except ValueError as e:
            logger.warning(f"Timeline validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Timeline error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["GRPCMonitorViewSet"]
