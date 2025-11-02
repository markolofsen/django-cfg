"""
gRPC Service Registry ViewSet.

Provides REST API endpoints for viewing registered gRPC services and their methods.
"""

from django.db import models
from django.db.models import Avg, Count, Max, Min
from django_cfg.mixins import AdminAPIMixin
from django_cfg.modules.django_logging import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import GRPCRequestLog
from ..serializers.service_registry import (
    MethodDetailSerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
    ServiceMethodsSerializer,
)
from ..services import ServiceDiscovery

logger = get_logger("grpc.services")


class GRPCServiceViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for gRPC service registry and management.

    Provides endpoints for:
    - List all registered services
    - Get service details
    - Get service methods
    - Get method details and statistics

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    @extend_schema(
        tags=["gRPC Services"],
        summary="List all services",
        description="Returns list of all registered gRPC services with basic statistics.",
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
        },
    )
    def list(self, request):
        """List all registered gRPC services."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)

            # Get registered services from discovery
            discovery = ServiceDiscovery()
            registered_services = discovery.get_registered_services()

            # Get statistics for each service
            services_list = []
            for service in registered_services:
                service_name = service.get("name")

                # Get stats from GRPCRequestLog
                stats = (
                    GRPCRequestLog.objects.filter(service_name=service_name)
                    .recent(hours)
                    .aggregate(
                        total=Count("id"),
                        successful=Count("id", filter=models.Q(status="success")),
                        avg_duration=Avg("duration_ms"),
                        last_activity=Max("created_at"),
                    )
                )

                # Calculate success rate
                total = stats["total"] or 0
                successful = stats["successful"] or 0
                success_rate = (successful / total * 100) if total > 0 else 0.0

                # Extract package name
                package = service_name.split(".")[0] if "." in service_name else ""

                services_list.append(
                    {
                        "name": service_name,
                        "full_name": service.get("full_name", f"/{service_name}"),
                        "package": package,
                        "methods_count": len(service.get("methods", [])),
                        "total_requests": total,
                        "success_rate": round(success_rate, 2),
                        "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
                        "last_activity_at": (
                            stats["last_activity"].isoformat()
                            if stats["last_activity"]
                            else None
                        ),
                    }
                )

            response_data = {
                "services": services_list,
                "total_services": len(services_list),
            }

            serializer = ServiceListSerializer(**response_data)
            return Response(serializer.model_dump())

        except Exception as e:
            logger.error(f"Service list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Services"],
        summary="Get service details",
        description="Returns detailed information about a specific gRPC service.",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Service name (e.g., myapp.UserService)",
                required=True,
            ),
        ],
        responses={
            200: ServiceDetailSerializer,
            404: {"description": "Service not found"},
        },
    )
    def retrieve(self, request, pk=None):
        """Get detailed information about a service."""
        try:
            service_name = pk  # pk is service_name in URL

            # Get service from discovery
            discovery = ServiceDiscovery()
            service = discovery.get_service_by_name(service_name)

            if not service:
                return Response(
                    {"error": f"Service '{service_name}' not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get statistics
            stats = GRPCRequestLog.objects.filter(service_name=service_name).aggregate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                errors=Count("id", filter=models.Q(status="error")),
                avg_duration=Avg("duration_ms"),
            )

            # Calculate success rate
            total = stats["total"] or 0
            successful = stats["successful"] or 0
            success_rate = (successful / total * 100) if total > 0 else 0.0

            # Get last 24h requests
            from datetime import timedelta

            from django.utils import timezone

            last_24h = timezone.now() - timedelta(hours=24)
            last_24h_count = GRPCRequestLog.objects.filter(
                service_name=service_name, created_at__gte=last_24h
            ).count()

            # Get recent errors
            recent_errors = list(
                GRPCRequestLog.objects.filter(
                    service_name=service_name,
                    status="error",
                )
                .order_by("-created_at")[:5]
                .values(
                    "method_name",
                    "error_message",
                    "grpc_status_code",
                    "created_at",
                )
            )

            # Format methods
            methods = []
            for method_name in service.get("methods", []):
                methods.append(
                    {
                        "name": method_name,
                        "full_name": f"/{service_name}/{method_name}",
                        "request_type": "",
                        "response_type": "",
                        "streaming": False,
                        "auth_required": False,
                    }
                )

            # Extract package
            package = service_name.split(".")[0] if "." in service_name else ""

            # Format response
            service_detail = {
                "name": service_name,
                "full_name": service.get("full_name", f"/{service_name}"),
                "package": package,
                "description": service.get("description", ""),
                "file_path": service.get("file_path", ""),
                "class_name": service.get("class_name", ""),
                "base_class": service.get("base_class", ""),
                "methods": methods,
                "stats": {
                    "total_requests": total,
                    "successful": successful,
                    "errors": stats["errors"] or 0,
                    "success_rate": round(success_rate, 2),
                    "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
                    "last_24h_requests": last_24h_count,
                },
                "recent_errors": [
                    {
                        "method": err["method_name"],
                        "error_message": err["error_message"] or "",
                        "grpc_status_code": err["grpc_status_code"] or "",
                        "occurred_at": err["created_at"].isoformat(),
                    }
                    for err in recent_errors
                ],
            }

            serializer = ServiceDetailSerializer(**service_detail)
            return Response(serializer.model_dump())

        except Exception as e:
            logger.error(f"Service detail error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Services"],
        summary="Get service methods",
        description="Returns list of methods for a specific service with statistics.",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Service name",
                required=True,
            ),
        ],
        responses={
            200: ServiceMethodsSerializer,
            404: {"description": "Service not found"},
        },
    )
    @action(detail=True, methods=["get"], url_path="methods")
    def methods(self, request, pk=None):
        """Get methods for a service."""
        try:
            service_name = pk

            # Get service from discovery
            discovery = ServiceDiscovery()
            service = discovery.get_service_by_name(service_name)

            if not service:
                return Response(
                    {"error": f"Service '{service_name}' not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get statistics for each method
            methods_list = []
            for method_name in service.get("methods", []):
                # Get durations for percentile calculation
                durations = list(
                    GRPCRequestLog.objects.filter(
                        service_name=service_name,
                        method_name=method_name,
                        duration_ms__isnull=False,
                    ).values_list("duration_ms", flat=True)
                )

                # Get aggregate stats
                stats = GRPCRequestLog.objects.filter(
                    service_name=service_name,
                    method_name=method_name,
                ).aggregate(
                    total=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    errors=Count("id", filter=models.Q(status="error")),
                    avg_duration=Avg("duration_ms"),
                )

                # Calculate percentiles
                p50, p95, p99 = self._calculate_percentiles(durations)

                # Calculate success rate
                total = stats["total"] or 0
                successful = stats["successful"] or 0
                success_rate = (successful / total * 100) if total > 0 else 0.0

                methods_list.append(
                    {
                        "name": method_name,
                        "full_name": f"/{service_name}/{method_name}",
                        "service_name": service_name,
                        "request_type": "",
                        "response_type": "",
                        "stats": {
                            "total_requests": total,
                            "successful": successful,
                            "errors": stats["errors"] or 0,
                            "success_rate": round(success_rate, 2),
                            "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
                            "p50_duration_ms": p50,
                            "p95_duration_ms": p95,
                            "p99_duration_ms": p99,
                        },
                    }
                )

            response_data = {
                "service_name": service_name,
                "methods": methods_list,
                "total_methods": len(methods_list),
            }

            serializer = ServiceMethodsSerializer(**response_data)
            return Response(serializer.model_dump())

        except Exception as e:
            logger.error(f"Service methods error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _calculate_percentiles(self, values):
        """Calculate p50, p95, p99 percentiles."""
        if not values:
            return 0.0, 0.0, 0.0

        sorted_values = sorted(values)
        n = len(sorted_values)

        p50_idx = int(n * 0.50)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)

        return (
            float(sorted_values[p50_idx] if p50_idx < n else 0),
            float(sorted_values[p95_idx] if p95_idx < n else 0),
            float(sorted_values[p99_idx] if p99_idx < n else 0),
        )


__all__ = ["GRPCServiceViewSet"]
