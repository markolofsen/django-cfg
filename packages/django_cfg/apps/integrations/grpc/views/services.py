"""
gRPC Service Registry ViewSet.

Provides REST API endpoints for viewing registered gRPC services and their methods.
"""

from django.db import models
from django.db.models import Avg, Count, Max, Min
from django_cfg.middleware.pagination import DefaultPagination
from django_cfg.mixins import AdminAPIMixin
from django_cfg.utils import get_logger
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
    ServiceSummarySerializer,
)
from ..services import ServiceRegistryManager

logger = get_logger("grpc.services")


class GRPCServiceViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    ViewSet for gRPC service registry and management.

    Provides endpoints for:
    - List all registered services
    - Get service details
    - Get service methods
    - Get method details and statistics

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    # Pagination for list endpoint
    pagination_class = DefaultPagination

    # Required for GenericViewSet
    queryset = GRPCRequestLog.objects.none()  # Placeholder
    serializer_class = ServiceSummarySerializer

    # Allow dots in service names (e.g., apps.CryptoService)
    lookup_value_regex = r'[^/]+'

    @extend_schema(
        tags=["gRPC Services"],
        summary="List all services",
        description="Returns paginated list of all registered gRPC services with basic statistics.",
        parameters=[
            OpenApiParameter(
                name="hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Statistics period in hours (default: 24)",
                required=False,
            ),
            # Note: page, page_size added automatically by pagination_class
        ],
        responses={
            200: ServiceSummarySerializer(many=True),
        },
    )
    def list(self, request):
        """List all registered gRPC services with pagination."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)

            # Use service registry manager
            registry = ServiceRegistryManager()

            # Get services with stats from service layer
            # Note: This will return empty list if server is not running,
            # but that's expected - services are only known when server is started
            services_list = registry.get_all_services_with_stats(hours=hours)

            # Paginate the services list (works with empty list too)
            page = self.paginate_queryset(services_list)
            if page is not None:
                serializer = ServiceSummarySerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # Fallback (no pagination)
            serializer = ServiceSummarySerializer(services_list, many=True)
            return Response(serializer.data)

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

            # Use service registry manager
            registry = ServiceRegistryManager()

            if not registry.is_server_running():
                return Response(
                    {"error": "gRPC server is not running"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            service = registry.get_service_by_name(service_name)
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

            serializer = ServiceDetailSerializer(data=service_detail)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

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

            # Use service registry manager
            registry = ServiceRegistryManager()

            if not registry.is_server_running():
                return Response(
                    {"error": "gRPC server is not running"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            service = registry.get_service_by_name(service_name)
            if not service:
                return Response(
                    {"error": f"Service '{service_name}' not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get methods with stats from service layer
            methods_list = registry.get_service_methods_with_stats(service_name)

            response_data = {
                "service_name": service_name,
                "methods": methods_list,
                "total_methods": len(methods_list),
            }

            serializer = ServiceMethodsSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Service methods error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["GRPCServiceViewSet"]
