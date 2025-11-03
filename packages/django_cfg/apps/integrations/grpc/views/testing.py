"""
gRPC Testing ViewSet.

Provides REST API endpoints for interactive gRPC method testing,
examples, and test logs.
"""

import json

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
    GRPCTestLogSerializer,
)
from ..services import TestingService

logger = get_logger("grpc.testing")


class GRPCTestingViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    ViewSet for gRPC method testing.

    Provides endpoints for:
    - Example payloads viewing
    - Test logs viewing
    - Method calling (placeholder for future implementation)

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    # Required for GenericViewSet
    queryset = GRPCRequestLog.objects.none()  # Placeholder, actual queries in actions
    serializer_class = GRPCTestLogSerializer  # Default serializer for schema

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

            service = TestingService()
            examples = service.get_examples(
                service_filter=service_filter,
                method_filter=method_filter,
            )

            response_data = {
                "examples": examples,
                "total_examples": len(examples),
            }

            serializer = GRPCExamplesListSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Examples fetch error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Testing"],
        summary="Get test logs",
        description="Returns logs from test gRPC calls. Uses standard DRF pagination.",
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
                description="Filter by status (success, error, etc.)",
                required=False,
            ),
        ],
        responses={
            200: GRPCTestLogSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="logs")
    def logs(self, request):
        """Get test logs."""
        try:
            service_filter = request.GET.get("service")
            method_filter = request.GET.get("method")
            status_filter = request.GET.get("status")

            service = TestingService()
            queryset = service.get_test_logs(
                service_filter=service_filter,
                method_filter=method_filter,
                status_filter=status_filter,
            )

            # Use DRF pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                # Serialize paginated data
                logs_list = []
                for log in page:
                    logs_list.append({
                        "request_id": log.request_id,
                        "service": log.service_name,
                        "method": log.method_name,
                        "status": log.status,
                        "grpc_status_code": log.grpc_status_code or "",
                        "error_message": log.error_message or "",
                        "duration_ms": log.duration_ms or 0,
                        "created_at": log.created_at.isoformat(),
                        "user": log.user.username if log.user else None,
                    })
                return self.get_paginated_response(logs_list)

            # No pagination (shouldn't happen with default pagination)
            logs_list = []
            for log in queryset[:100]:  # Safety limit
                logs_list.append({
                    "request_id": log.request_id,
                    "service": log.service_name,
                    "method": log.method_name,
                    "status": log.status,
                    "grpc_status_code": log.grpc_status_code or "",
                    "error_message": log.error_message or "",
                    "duration_ms": log.duration_ms or 0,
                    "created_at": log.created_at.isoformat(),
                    "user": log.user.username if log.user else None,
                })
            return Response({"logs": logs_list, "count": len(logs_list)})

        except Exception as e:
            logger.error(f"Test logs error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Testing"],
        summary="Call gRPC method",
        description=(
            "Interactive gRPC method calling using dynamic invocation. "
            "Uses gRPC Reflection API to discover and call methods without compiled stubs."
        ),
        request=GRPCCallRequestSerializer,
        responses={
            200: GRPCCallResponseSerializer,
            400: {"description": "Invalid request"},
            404: {"description": "Service or method not found"},
            500: {"description": "gRPC call failed"},
        },
    )
    @action(detail=False, methods=["post"], url_path="call")
    def call_method(self, request):
        """
        Call a gRPC method interactively.

        Request body:
            {
                "service": "apps.CryptoService",
                "method": "GetCoin",
                "request": {"symbol": "BTC"},
                "metadata": {"authorization": "Bearer token"},
                "timeout": 5.0
            }

        Uses gRPC Reflection API for dynamic invocation.
        Logs all calls to GRPCRequestLog for history tracking.
        """
        from uuid import uuid4
        from django.utils import timezone

        try:
            # Validate request - DRF validation
            serializer = GRPCCallRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            service_name = data["service"]
            method_name = data["method"]
            request_data = data.get("payload", {})
            metadata = data.get("metadata", {})
            timeout_ms = data.get("timeout_ms", 5000)
            timeout = timeout_ms / 1000.0  # Convert to seconds

            # Generate request ID
            request_id = str(uuid4())

            # Create log entry (pending)
            log = GRPCRequestLog.objects.create(
                request_id=request_id,
                service_name=service_name,
                method_name=method_name,
                full_method=f"/{service_name}/{method_name}",
                status="pending",
                user=request.user if request.user.is_authenticated else None,
                is_authenticated=request.user.is_authenticated,
                request_data=request_data,
            )

            # Call method via service
            start_time = timezone.now()

            service = TestingService()
            result = service.call_method(
                service_name=service_name,
                method_name=method_name,
                request_data=request_data,
                metadata=metadata,
                timeout=timeout,
            )

            end_time = timezone.now()

            # Update log
            log.status = "success" if result["success"] else "error"
            log.grpc_status_code = result["grpc_status_code"]
            log.duration_ms = result["duration_ms"]
            log.response_data = result.get("response") or {}
            log.error_message = result.get("error_message") or ""
            log.completed_at = end_time
            log.save()

            # Construct full response using GRPCCallResponseSerializer
            response_data = result.get("response")
            if response_data and isinstance(response_data, dict):
                response_data = json.dumps(response_data)

            response_data_dict = {
                "success": result["success"],
                "request_id": request_id,
                "service": result["service"],
                "method": result["method"],
                "status": log.status,
                "grpc_status_code": result["grpc_status_code"],
                "duration_ms": result["duration_ms"],
                "response": response_data,
                "error": result.get("error_message"),
                "metadata": {},
                "timestamp": end_time.isoformat(),
            }

            response_serializer = GRPCCallResponseSerializer(data=response_data_dict)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"gRPC call endpoint error: {e}", exc_info=True)
            return Response(
                {
                    "success": False,
                    "error": "Internal server error",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["GRPCTestingViewSet"]
