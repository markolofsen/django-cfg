"""
Monitoring Service.

Provides business logic for gRPC monitoring and statistics.
"""

from datetime import datetime
from typing import Dict, List, Optional

from django.conf import settings
from django.db import models
from django.db.models import Avg, Count, Max
from django.db.models.functions import TruncDay, TruncHour
from django_cfg.modules.django_logging import get_logger

from ..models import GRPCRequestLog, GRPCServerStatus
from ..serializers import (
    GRPCHealthCheckSerializer,
    GRPCOverviewStatsSerializer,
    MethodStatsSerializer,
    MonitoringServiceStatsSerializer,
)
from ..serializers.service_registry import RecentRequestSerializer

logger = get_logger("grpc.monitoring_service")


class MonitoringService:
    """
    Service for gRPC monitoring operations.

    Provides methods to retrieve health status, statistics, and monitoring data.
    """

    def get_health_status(self) -> Dict:
        """
        Get gRPC server health status.

        Returns:
            Dictionary with health status data

        Example:
            >>> service = MonitoringService()
            >>> health = service.get_health_status()
            >>> health['status']
            'healthy'
        """
        grpc_server_config = getattr(settings, "GRPC_SERVER", {})

        if not grpc_server_config:
            raise ValueError("gRPC not configured")

        # Check if server is actually running
        current_server = GRPCServerStatus.objects.get_current_server()
        is_running = current_server and current_server.is_running

        # Ensure enabled is always boolean, not None
        enabled = bool(is_running) if is_running is not None else False

        health_data = GRPCHealthCheckSerializer(
            status="healthy" if enabled else "stopped",
            server_host=grpc_server_config.get("host", "[::]"),
            server_port=grpc_server_config.get("port", 50051),
            enabled=enabled,
            timestamp=datetime.now().isoformat(),
        )

        return health_data.model_dump()

    def get_overview_statistics(self, hours: int = 24) -> Dict:
        """
        Get overview statistics for gRPC requests.

        Args:
            hours: Statistics period in hours (1-168)

        Returns:
            Dictionary with overview statistics

        Example:
            >>> service = MonitoringService()
            >>> stats = service.get_overview_statistics(hours=24)
            >>> stats['total_requests']
            1000
        """
        hours = min(max(hours, 1), 168)  # 1 hour to 1 week

        stats = GRPCRequestLog.objects.get_statistics(hours=hours)
        stats["period_hours"] = hours

        overview = GRPCOverviewStatsSerializer(**stats)
        return overview.model_dump()

    def get_recent_requests(
        self,
        service_name: Optional[str] = None,
        method_name: Optional[str] = None,
        status_filter: Optional[str] = None,
    ):
        """
        Get recent gRPC requests queryset.

        Args:
            service_name: Filter by service name
            method_name: Filter by method name
            status_filter: Filter by status (success/error)

        Returns:
            Queryset of GRPCRequestLog (pagination handled by DRF)

        Example:
            >>> service = MonitoringService()
            >>> queryset = service.get_recent_requests(status_filter='error')
            >>> queryset.count()
            25
        """
        queryset = GRPCRequestLog.objects.all()

        # Apply filters
        if service_name:
            queryset = queryset.filter(service_name=service_name)
        if method_name:
            queryset = queryset.filter(method_name=method_name)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")

    def get_service_statistics(self, hours: int = 24) -> List[Dict]:
        """
        Get statistics per service.

        Args:
            hours: Statistics period in hours

        Returns:
            List of service statistics

        Example:
            >>> service = MonitoringService()
            >>> services = service.get_service_statistics(hours=24)
            >>> services[0]['service_name']
            'apps.CryptoService'
        """
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
            service_data = MonitoringServiceStatsSerializer(
                service_name=stats["service_name"],
                total=stats["total"],
                successful=stats["successful"],
                errors=stats["errors"],
                avg_duration_ms=round(stats["avg_duration_ms"] or 0, 2),
                last_activity_at=(
                    stats["last_activity_at"].isoformat()
                    if stats["last_activity_at"]
                    else None
                ),
            )
            services_list.append(service_data.model_dump())

        return services_list

    def get_method_statistics(
        self, service_name: Optional[str] = None, hours: int = 24
    ) -> List[Dict]:
        """
        Get statistics per method.

        Args:
            service_name: Filter by service name
            hours: Statistics period in hours

        Returns:
            List of method statistics

        Example:
            >>> service = MonitoringService()
            >>> methods = service.get_method_statistics(service_name='apps.CryptoService')
            >>> methods[0]['method_name']
            'GetCoin'
        """
        hours = min(max(hours, 1), 168)

        queryset = GRPCRequestLog.objects.recent(hours)

        if service_name:
            queryset = queryset.filter(service_name=service_name)

        # Get method statistics
        method_stats = (
            queryset.values("service_name", "method_name")
            .annotate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                errors=Count("id", filter=models.Q(status="error")),
                avg_duration_ms=Avg("duration_ms"),
                last_activity_at=Max("created_at"),  # Add missing field
            )
            .order_by("-total")
        )

        methods_list = []
        for stats in method_stats:
            method_data = MethodStatsSerializer(
                service_name=stats["service_name"],
                method_name=stats["method_name"],
                total=stats["total"],
                successful=stats["successful"],
                errors=stats["errors"],
                avg_duration_ms=round(stats["avg_duration_ms"] or 0, 2),
                last_activity_at=(
                    stats["last_activity_at"].isoformat()
                    if stats["last_activity_at"]
                    else None
                ),
            )
            methods_list.append(method_data.model_dump())

        return methods_list

    def get_timeline_data(self, hours: int = 24, granularity: str = "hour") -> List[Dict]:
        """
        Get timeline data for requests.

        Args:
            hours: Period in hours
            granularity: 'hour' or 'day'

        Returns:
            List of timeline data points

        Example:
            >>> service = MonitoringService()
            >>> timeline = service.get_timeline_data(hours=24, granularity='hour')
            >>> timeline[0]['timestamp']
            '2025-01-01T12:00:00'
        """
        hours = min(max(hours, 1), 168)

        # Choose truncation function
        if granularity == "day" or hours > 48:
            trunc_func = TruncDay
            time_format = "%Y-%m-%d"
        else:
            trunc_func = TruncHour
            time_format = "%Y-%m-%d %H:00"

        # Get timeline data
        timeline_data = (
            GRPCRequestLog.objects.recent(hours)
            .annotate(period=trunc_func("created_at"))
            .values("period")
            .annotate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                errors=Count("id", filter=models.Q(status="error")),
                avg_duration=Avg("duration_ms"),
            )
            .order_by("period")
        )

        timeline_list = []
        for data in timeline_data:
            timeline_list.append({
                "timestamp": data["period"].strftime(time_format),
                "total": data["total"],
                "successful": data["successful"],
                "errors": data["errors"],
                "avg_duration_ms": round(data["avg_duration"] or 0, 2),
            })

        return timeline_list


__all__ = ["MonitoringService"]
