"""
gRPC Testing ViewSet.

Provides REST API endpoints for interactive gRPC method testing,
examples, and test logs.
"""

from django_cfg.mixins import AdminAPIMixin
from django_cfg.modules.django_logging import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import GRPCRequestLog
from ..serializers.testing import (
    GRPCCallRequestSerializer,
    GRPCCallResponseSerializer,
    GRPCExamplesListSerializer,
    GRPCTestLogsSerializer,
)
from ..services import ServiceDiscovery
from ..testing import get_example

logger = get_logger("grpc.testing")


class GRPCTestingViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for gRPC method testing.

    Provides endpoints for:
    - Example payloads viewing
    - Test logs viewing
    - Method calling (placeholder for future implementation)

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    @extend_schema(
        tags=["gRPC Testing"],
        summary="Get example payloads",
        description="Returns example payloads for testing gRPC methods.",
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
        ],
        responses={
            200: GRPCExamplesListSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="examples")
    def examples(self, request):
        """Get example payloads for testing."""
        try:
            service_filter = request.GET.get("service")
            method_filter = request.GET.get("method")

            # Get registered services
            discovery = ServiceDiscovery()
            services = discovery.get_registered_services()

            examples = []
            for service in services:
                service_name = service.get("class_name", "")
                if not service_name:
                    continue

                # Filter by service if specified
                if service_filter and service_name != service_filter:
                    continue

                for method_name in service.get("methods", []):
                    # Filter by method if specified
                    if method_filter and method_name != method_filter:
                        continue

                    # Get example from registry
                    example = get_example(service_name, method_name)
                    if example:
                        examples.append(
                            {
                                "service": service_name,
                                "method": method_name,
                                "description": example.get(
                                    "description", f"{method_name} method"
                                ),
                                "payload_example": example.get("payload", {}),
                                "expected_response": example.get(
                                    "expected_response", {}
                                ),
                                "metadata_example": example.get("metadata", {}),
                            }
                        )

            response_data = {
                "examples": examples,
                "total_examples": len(examples),
            }

            serializer = GRPCExamplesListSerializer(**response_data)
            return Response(serializer.model_dump())

        except Exception as e:
            logger.error(f"Examples fetch error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Testing"],
        summary="Get test logs",
        description="Returns logs from test gRPC calls.",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of logs to return (default: 50, max: 200)",
                required=False,
            ),
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Offset for pagination (default: 0)",
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
                description="Filter by status (success, error, etc.)",
                required=False,
            ),
        ],
        responses={
            200: GRPCTestLogsSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="logs")
    def logs(self, request):
        """Get test logs."""
        try:
            limit = min(int(request.GET.get("limit", 50)), 200)
            offset = int(request.GET.get("offset", 0))
            service_filter = request.GET.get("service")
            method_filter = request.GET.get("method")
            status_filter = request.GET.get("status")

            # Query logs
            queryset = GRPCRequestLog.objects.all()

            if service_filter:
                queryset = queryset.filter(service_name__icontains=service_filter)
            if method_filter:
                queryset = queryset.filter(method_name__icontains=method_filter)
            if status_filter:
                queryset = queryset.filter(status=status_filter)

            # Get total count
            total = queryset.count()

            # Get logs with pagination
            logs = list(
                queryset.order_by("-created_at")[offset : offset + limit].values(
                    "request_id",
                    "service_name",
                    "method_name",
                    "status",
                    "grpc_status_code",
                    "error_message",
                    "duration_ms",
                    "created_at",
                    "user__username",
                )
            )

            # Format logs
            logs_list = []
            for log in logs:
                logs_list.append(
                    {
                        "request_id": log["request_id"],
                        "service": log["service_name"],
                        "method": log["method_name"],
                        "status": log["status"],
                        "grpc_status_code": log["grpc_status_code"],
                        "error_message": log["error_message"],
                        "duration_ms": log["duration_ms"],
                        "created_at": log["created_at"].isoformat(),
                        "user": log["user__username"],
                    }
                )

            response_data = {
                "logs": logs_list,
                "count": len(logs_list),
                "total_available": total,
                "has_more": (offset + limit) < total,
            }

            serializer = GRPCTestLogsSerializer(**response_data)
            return Response(serializer.model_dump())

        except Exception as e:
            logger.error(f"Test logs error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Testing"],
        summary="Call gRPC method (placeholder)",
        description=(
            "Interactive gRPC method calling. "
            "NOTE: This is a placeholder endpoint. "
            "Dynamic gRPC invocation is not yet implemented. "
            "Use grpcurl or implement Phase 4 for this functionality."
        ),
        request=GRPCCallRequestSerializer,
        responses={
            501: {"description": "Not implemented"},
            200: GRPCCallResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="call")
    def call_method(self, request):
        """
        Call a gRPC method interactively.

        NOTE: This is a placeholder. Dynamic gRPC invocation requires:
        1. gRPC Reflection API implementation
        2. Dynamic message creation from JSON
        3. Generic gRPC channel handling

        For now, use grpcurl for interactive testing:
            grpcurl -plaintext -d '{"user_id": 123}' \\
                localhost:50051 myapp.UserService/GetUser

        To implement this feature, see:
        - @refactoring/03_TESTING_API.md (Phase 4)
        - @refactoring/05_IMPLEMENTATION_PLAN.md
        """
        return Response(
            {
                "error": "Not implemented",
                "message": (
                    "Dynamic gRPC invocation is not yet implemented. "
                    "This requires Phase 4 implementation with gRPC Reflection API. "
                    "For now, please use grpcurl for interactive testing."
                ),
                "documentation": {
                    "grpcurl": "https://github.com/fullstorydev/grpcurl",
                    "implementation_guide": "@refactoring/03_TESTING_API.md",
                },
                "alternative": (
                    "grpcurl -plaintext -d '{\"field\": \"value\"}' "
                    "localhost:50051 ServiceName/MethodName"
                ),
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


__all__ = ["GRPCTestingViewSet"]
