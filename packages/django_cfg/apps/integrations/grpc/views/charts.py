"""
gRPC Charts ViewSet.

Provides REST API endpoints for chart data and statistics visualization.
Uses ChartGeneratorService for all data generation logic.
"""

from django_cfg.mixins import AdminAPIMixin
from django_cfg.modules.django_logging import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers.charts import (
    DashboardChartsSerializer,
    ErrorDistributionChartSerializer,
    RequestVolumeChartSerializer,
    ResponseTimeChartSerializer,
    ServerLifecycleChartSerializer,
    ServerUptimeChartSerializer,
    ServiceActivityChartSerializer,
)
from ..services.rendering.charts import ChartGeneratorService

logger = get_logger("grpc.charts")


class GRPCChartsViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for gRPC charts and statistics visualization.

    Provides endpoints for:
    - Server uptime over time
    - Request volume trends
    - Response time metrics
    - Service activity comparison
    - Server lifecycle events
    - Error distribution
    - Combined dashboard data

    All endpoints support time range filtering via 'hours' query parameter.
    """

    TIME_RANGE_PARAM = OpenApiParameter(
        name="hours",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Time range in hours (default: 24, max: 720)",
        required=False,
    )

    def _validate_hours(self, hours_str: str) -> int:
        """Validate and normalize hours parameter."""
        try:
            hours = int(hours_str)
            return min(max(hours, 1), 720)  # 1 hour to 30 days
        except (ValueError, TypeError):
            return 24

    @extend_schema(
        tags=["gRPC Charts"],
        summary="Get server uptime chart data",
        description="Returns time-series data showing number of running servers over time.",
        parameters=[TIME_RANGE_PARAM],
        responses={200: ServerUptimeChartSerializer},
    )
    @action(detail=False, methods=["get"], url_path="server-uptime")
    def server_uptime(self, request):
        """Get server uptime chart data."""
        try:
            hours = self._validate_hours(request.GET.get("hours", "24"))
            data = ChartGeneratorService.generate_server_uptime_data(hours)
            serializer = ServerUptimeChartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Server uptime chart error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Charts"],
        summary="Get request volume chart data",
        description="Returns time-series data showing request volume and success rates.",
        parameters=[TIME_RANGE_PARAM],
        responses={200: RequestVolumeChartSerializer},
    )
    @action(detail=False, methods=["get"], url_path="request-volume")
    def request_volume(self, request):
        """Get request volume chart data."""
        try:
            hours = self._validate_hours(request.GET.get("hours", "24"))
            data = ChartGeneratorService.generate_request_volume_data(hours)
            serializer = RequestVolumeChartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Request volume chart error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Charts"],
        summary="Get response time chart data",
        description="Returns time-series data showing response time statistics (avg, P50, P95, P99).",
        parameters=[TIME_RANGE_PARAM],
        responses={200: ResponseTimeChartSerializer},
    )
    @action(detail=False, methods=["get"], url_path="response-time")
    def response_time(self, request):
        """Get response time chart data."""
        try:
            hours = self._validate_hours(request.GET.get("hours", "24"))
            data = ChartGeneratorService.generate_response_time_data(hours)
            serializer = ResponseTimeChartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Response time chart error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Charts"],
        summary="Get service activity chart data",
        description="Returns comparison data showing activity across all services.",
        parameters=[TIME_RANGE_PARAM],
        responses={200: ServiceActivityChartSerializer},
    )
    @action(detail=False, methods=["get"], url_path="service-activity")
    def service_activity(self, request):
        """Get service activity chart data."""
        try:
            hours = self._validate_hours(request.GET.get("hours", "24"))
            data = ChartGeneratorService.generate_service_activity_data(hours)
            serializer = ServiceActivityChartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Service activity chart error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Charts"],
        summary="Get server lifecycle events",
        description="Returns timeline of server start/stop/error events.",
        parameters=[TIME_RANGE_PARAM],
        responses={200: ServerLifecycleChartSerializer},
    )
    @action(detail=False, methods=["get"], url_path="server-lifecycle")
    def server_lifecycle(self, request):
        """Get server lifecycle events."""
        try:
            hours = self._validate_hours(request.GET.get("hours", "24"))
            data = ChartGeneratorService.generate_server_lifecycle_data(hours)
            serializer = ServerLifecycleChartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Server lifecycle chart error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Charts"],
        summary="Get error distribution chart data",
        description="Returns distribution of error types across services.",
        parameters=[TIME_RANGE_PARAM],
        responses={200: ErrorDistributionChartSerializer},
    )
    @action(detail=False, methods=["get"], url_path="error-distribution")
    def error_distribution(self, request):
        """Get error distribution chart data."""
        try:
            hours = self._validate_hours(request.GET.get("hours", "24"))
            data = ChartGeneratorService.generate_error_distribution_data(hours)
            serializer = ErrorDistributionChartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error distribution chart error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Charts"],
        summary="Get all dashboard charts data",
        description="Returns combined data for all charts in one request (optimized).",
        parameters=[TIME_RANGE_PARAM],
        responses={200: DashboardChartsSerializer},
    )
    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        """Get all dashboard charts data in one request."""
        try:
            hours = self._validate_hours(request.GET.get("hours", "24"))
            data = ChartGeneratorService.generate_dashboard_data(hours)
            serializer = DashboardChartsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Dashboard charts error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["GRPCChartsViewSet"]
