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
from django_cfg.modules.django_logging import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import GRPCRequestLog
from ..serializers import (
    HealthCheckSerializer,
    MethodListSerializer,
    MethodStatsSerializer,
    OverviewStatsSerializer,
    RecentRequestsSerializer,
    ServiceListSerializer,
    ServiceStatsSerializer,
)

logger = get_logger("grpc.monitoring")


class GRPCMonitorViewSet(AdminAPIMixin, viewsets.ViewSet):
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

    @extend_schema(
        tags=["gRPC Monitoring"],
        summary="Get gRPC health status",
        description="Returns the current health status of the gRPC server.",
        responses={
            200: HealthCheckSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=["get"], url_path="health")
    def health(self, request):
        """Get health status of gRPC server."""
        try:
            grpc_server_config = getattr(settings, "GRPC_SERVER", {})
            grpc_framework_config = getattr(settings, "GRPC_FRAMEWORK", {})

            if not grpc_server_config:
                return Response(
                    {"error": "gRPC not configured"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            health_data = {
                "status": "healthy",
                "server_host": grpc_server_config.get("host", "[::]"),
                "server_port": grpc_server_config.get("port", 50051),
                "enabled": True,
                "timestamp": datetime.now().isoformat(),
            }

            serializer = HealthCheckSerializer(**health_data)
            return Response(serializer.model_dump())

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
            200: OverviewStatsSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="overview")
    def overview(self, request):
        """Get overview statistics for gRPC requests."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)  # 1 hour to 1 week

            stats = GRPCRequestLog.objects.get_statistics(hours=hours)
            stats["period_hours"] = hours

            serializer = OverviewStatsSerializer(**stats)
            return Response(serializer.model_dump())

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
        description="Returns a list of recent gRPC requests with their details.",
        parameters=[
            OpenApiParameter(
                name="count",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of requests to return (default: 50, max: 200)",
                required=False,
            ),
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
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Offset for pagination (default: 0)",
                required=False,
            ),
        ],
        responses={
            200: RecentRequestsSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="requests")
    def requests(self, request):
        """Get recent gRPC requests."""
        try:
            count = int(request.GET.get("count", 50))
            count = min(count, 200)  # Max 200

            service_filter = request.GET.get("service")
            method_filter = request.GET.get("method")
            status_filter = request.GET.get("status")
            offset = int(request.GET.get("offset", 0))

            queryset = GRPCRequestLog.objects.all()

            if service_filter:
                queryset = queryset.filter(service_name=service_filter)

            if method_filter:
                queryset = queryset.filter(method_name=method_filter)

            if status_filter and status_filter in ["success", "error", "timeout", "pending", "cancelled"]:
                queryset = queryset.filter(status=status_filter)

            # Get total count before slicing
            total = queryset.count()

            # Apply offset and limit
            requests_list = list(
                queryset.order_by("-created_at")[offset:offset + count].values(
                    "request_id",
                    "service_name",
                    "method_name",
                    "full_method",
                    "status",
                    "grpc_status_code",
                    "is_authenticated",
                    "duration_ms",
                    "created_at",
                    "completed_at",
                    "error_message",
                    "user__username",
                )
            )

            # Convert datetime to ISO format
            for req in requests_list:
                if req["created_at"]:
                    req["created_at"] = req["created_at"].isoformat()
                if req["completed_at"]:
                    req["completed_at"] = req["completed_at"].isoformat()

            response_data = {
                "requests": requests_list,
                "count": len(requests_list),
                "total_available": total,
                "offset": offset,
                "has_more": (offset + count) < total,
            }

            serializer = RecentRequestsSerializer(**response_data)
            return Response(serializer.model_dump())

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
        summary="Get service statistics",
        description="Returns statistics grouped by service.",
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
            200: ServiceListSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="services")
    def services(self, request):
        """Get statistics per service."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)

            # Get service statistics
            service_stats = (
                GRPCRequestLog.objects.recent(hours)
                .values("service_name")
                .annotate(
                    total=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    errors=Count("id", filter=models.Q(status="error")),
                    avg_duration_ms=Avg("duration_ms"),
                    last_activity_at=Max("created_at"),
                )
                .order_by("-total")
            )

            services_list = []
            for stats in service_stats:
                services_list.append(
                    ServiceStatsSerializer(
                        service_name=stats["service_name"],
                        total=stats["total"],
                        successful=stats["successful"],
                        errors=stats["errors"],
                        avg_duration_ms=round(stats["avg_duration_ms"] or 0, 2),
                        last_activity_at=stats["last_activity_at"].isoformat() if stats["last_activity_at"] else None,
                    )
                )

            response_data = {
                "services": [svc.model_dump() for svc in services_list],
                "total_services": len(services_list),
            }

            serializer = ServiceListSerializer(**response_data)
            return Response(serializer.model_dump())

        except ValueError as e:
            logger.warning(f"Service stats validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Service stats error: {e}", exc_info=True)
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
    @action(detail=False, methods=["get"], url_path="methods")
    def methods(self, request):
        """Get statistics per method."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)
            service_filter = request.GET.get("service")

            # Get method statistics
            queryset = GRPCRequestLog.objects.recent(hours)

            if service_filter:
                queryset = queryset.filter(service_name=service_filter)

            method_stats = (
                queryset
                .values("service_name", "method_name")
                .annotate(
                    total=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    errors=Count("id", filter=models.Q(status="error")),
                    avg_duration_ms=Avg("duration_ms"),
                    last_activity_at=Max("created_at"),
                )
                .order_by("-total")
            )

            methods_list = []
            for stats in method_stats:
                methods_list.append(
                    MethodStatsSerializer(
                        method_name=stats["method_name"],
                        service_name=stats["service_name"],
                        total=stats["total"],
                        successful=stats["successful"],
                        errors=stats["errors"],
                        avg_duration_ms=round(stats["avg_duration_ms"] or 0, 2),
                        last_activity_at=stats["last_activity_at"].isoformat() if stats["last_activity_at"] else None,
                    )
                )

            response_data = {
                "methods": [method.model_dump() for method in methods_list],
                "total_methods": len(methods_list),
            }

            serializer = MethodListSerializer(**response_data)
            return Response(serializer.model_dump())

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
            hours = min(max(hours, 1), 168)
            interval = request.GET.get("interval", "hour")

            if interval not in ["hour", "day"]:
                interval = "hour"

            # Determine truncation function
            trunc_func = TruncHour if interval == "hour" else TruncDay

            # Get timeline data
            timeline_data = (
                GRPCRequestLog.objects.recent(hours)
                .annotate(period=trunc_func("created_at"))
                .values("period")
                .annotate(
                    count=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    errors=Count("id", filter=models.Q(status="error")),
                    timeout=Count("id", filter=models.Q(status="timeout")),
                    cancelled=Count("id", filter=models.Q(status="cancelled")),
                )
                .order_by("period")
            )

            timeline_list = []
            for item in timeline_data:
                timeline_list.append({
                    "timestamp": item["period"].isoformat(),
                    "count": item["count"],
                    "successful": item["successful"],
                    "errors": item["errors"],
                    "timeout": item["timeout"],
                    "cancelled": item["cancelled"],
                })

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
