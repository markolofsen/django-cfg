"""
Monitoring Service.

Provides business logic for gRPC monitoring and statistics.
"""

from datetime import datetime
from typing import Dict, List, Optional

from django.db import models
from django.db.models import Avg, Count, Max
from django.db.models.functions import TruncDay, TruncHour
from django_cfg.utils import get_logger

from ...models import GRPCRequestLog, GRPCServerStatus
from ..management.config_helper import get_grpc_server_config

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
        grpc_server_config = get_grpc_server_config()

        if not grpc_server_config:
            raise ValueError("gRPC not configured")

        # Check if server is actually running
        current_server = GRPCServerStatus.objects.get_current_server()
        is_running = current_server and current_server.is_running

        # Ensure enabled is always boolean, not None
        enabled = bool(is_running) if is_running is not None else False

        return {
            "status": "healthy" if enabled else "stopped",
            "server_host": grpc_server_config.host,
            "server_port": grpc_server_config.port,
            "enabled": enabled,
            "timestamp": datetime.now().isoformat(),
        }

    def get_overview_statistics(self, hours: int = 24) -> Dict:
        """
        Get overview statistics for gRPC requests with server information.

        Args:
            hours: Statistics period in hours (1-168)

        Returns:
            Dictionary with overview statistics and server info

        Example:
            >>> service = MonitoringService()
            >>> stats = service.get_overview_statistics(hours=24)
            >>> stats['total']
            1000
            >>> stats['server']['is_running']
            True
        """
        hours = min(max(hours, 1), 168)  # 1 hour to 1 week

        # Get request statistics
        stats = GRPCRequestLog.objects.get_statistics(hours=hours)
        stats["period_hours"] = hours

        # Get server information
        server_info = self._get_server_info_for_overview(hours=hours)
        stats["server"] = server_info

        return stats

    def _get_server_info_for_overview(self, hours: int) -> Dict:
        """
        Get server information for overview endpoint.

        Args:
            hours: Statistics period for service stats

        Returns:
            Dictionary with server information including services
        """
        from ..discovery.discovery import ServiceDiscovery

        # Get current server status
        current_server = GRPCServerStatus.objects.get_current_server()

        if not current_server:
            # No server running
            grpc_server_config = get_grpc_server_config()
            return {
                "status": "stopped",
                "is_running": False,
                "host": grpc_server_config.host if grpc_server_config else "[::]",
                "port": grpc_server_config.port if grpc_server_config else 50051,
                "address": f"{grpc_server_config.host}:{grpc_server_config.port}" if grpc_server_config else "[::]:50051",
                "pid": None,
                "started_at": None,
                "uptime_seconds": 0,
                "uptime_display": "Not running",
                "registered_services_count": 0,
                "enable_reflection": False,
                "enable_health_check": False,
                "last_heartbeat": None,
                "services": [],
                "services_healthy": True,
            }

        # Get service statistics for the period
        service_stats_qs = (
            GRPCRequestLog.objects.recent(hours)
            .values("service_name")
            .annotate(
                total=Count("id"),
                errors=Count("id", filter=models.Q(status="error")),
            )
        )

        # Create service stats lookup
        service_stats_lookup = {
            stat["service_name"]: stat for stat in service_stats_qs
        }

        # Get registered services from service discovery
        discovery = ServiceDiscovery()
        registered_services = discovery.get_registered_services()

        # Build services list with stats
        services_list = []
        total_errors = 0

        for service in registered_services:
            service_name = service.get("name", "")
            full_name = service.get("full_name", service_name)
            methods = service.get("methods", [])

            # Get stats for this service
            stats = service_stats_lookup.get(full_name, {"total": 0, "errors": 0})
            request_count = stats.get("total", 0)
            error_count = stats.get("errors", 0)
            success_rate = (
                ((request_count - error_count) / request_count * 100)
                if request_count > 0
                else 100.0
            )

            total_errors += error_count

            services_list.append({
                "name": service_name,
                "full_name": full_name,
                "methods_count": len(methods),
                "request_count": request_count,
                "error_count": error_count,
                "success_rate": round(success_rate, 2),
            })

        # Sort by request count
        services_list.sort(key=lambda x: x["request_count"], reverse=True)

        # Determine if all services are healthy (no errors in period)
        services_healthy = total_errors == 0

        return {
            "status": current_server.status,
            "is_running": current_server.is_running,
            "host": current_server.host,
            "port": current_server.port,
            "address": current_server.address,
            "pid": current_server.pid,
            "started_at": current_server.started_at,
            "uptime_seconds": current_server.uptime_seconds,
            "uptime_display": current_server.uptime_display,
            "registered_services_count": len(services_list),
            "enable_reflection": current_server.enable_reflection,
            "enable_health_check": current_server.enable_health_check,
            "last_heartbeat": current_server.last_heartbeat,
            "services": services_list,
            "services_healthy": services_healthy,
        }

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
        queryset = GRPCRequestLog.objects.select_related("user", "api_key").all()

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
            service_data = {
                "service_name": stats["service_name"],
                "total": stats["total"],
                "successful": stats["successful"],
                "errors": stats["errors"],
                "avg_duration_ms": round(stats["avg_duration_ms"] or 0, 2),
                "last_activity_at": (
                    stats["last_activity_at"].isoformat()
                    if stats["last_activity_at"]
                    else None
                ),
            }
            services_list.append(service_data)

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
            method_data = {
                "service_name": stats["service_name"],
                "method_name": stats["method_name"],
                "total": stats["total"],
                "successful": stats["successful"],
                "errors": stats["errors"],
                "avg_duration_ms": round(stats["avg_duration_ms"] or 0, 2),
                "last_activity_at": (
                    stats["last_activity_at"].isoformat()
                    if stats["last_activity_at"]
                    else None
                ),
            }
            methods_list.append(method_data)

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
