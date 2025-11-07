"""
Chart data generation service for gRPC monitoring.

This service handles the business logic for generating chart data
from GRPCRequestLog and GRPCServerStatus models.
"""

from datetime import timedelta
from typing import Dict, List, Tuple

from django.db import models
from django.db.models import Avg, Count, Max, Min, Q
from django.db.models.functions import TruncDay, TruncHour
from django.utils import timezone

from ...models import GRPCRequestLog, GRPCServerStatus


class ChartGeneratorService:
    """Service for generating chart data from gRPC logs and server status."""

    @staticmethod
    def get_time_range(hours: int) -> Tuple:
        """
        Get time range for queries.

        Args:
            hours: Number of hours to look back

        Returns:
            Tuple of (start_time, end_time)
        """
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        return start_time, end_time

    @staticmethod
    def determine_granularity(hours: int) -> str:
        """
        Determine appropriate data granularity based on time range.

        Args:
            hours: Time range in hours

        Returns:
            Granularity string: "hour", "day", or "week"
        """
        if hours <= 24:
            return "hour"
        elif hours <= 168:  # 1 week
            return "day"
        else:
            return "week"

    @staticmethod
    def get_time_delta(granularity: str) -> timedelta:
        """Get timedelta for given granularity."""
        if granularity == "hour":
            return timedelta(hours=1)
        elif granularity == "day":
            return timedelta(days=1)
        else:  # week
            return timedelta(weeks=1)

    @classmethod
    def generate_server_uptime_data(cls, hours: int = 24) -> Dict:
        """
        Generate server uptime chart data.

        Args:
            hours: Time range in hours

        Returns:
            Dictionary with uptime data points and statistics
        """
        start_time, end_time = cls.get_time_range(hours)
        granularity = cls.determine_granularity(hours)
        time_delta = cls.get_time_delta(granularity)

        # Get all server records in time range
        servers_in_range = list(
            GRPCServerStatus.objects.filter(
                started_at__lte=end_time,
            )
            .filter(
                Q(stopped_at__gte=start_time) | Q(stopped_at__isnull=True)
            )
            .values("address", "started_at", "stopped_at")
        )

        # Generate time series
        data_points = []
        current_time = start_time

        while current_time <= end_time:
            # Count servers running at this time
            running_servers = []

            for server in servers_in_range:
                server_started = server["started_at"]
                server_stopped = server["stopped_at"] or timezone.now()

                if server_started <= current_time <= server_stopped:
                    running_servers.append(server["address"])

            data_points.append({
                "timestamp": current_time.isoformat(),
                "server_count": len(running_servers),
                "servers": list(set(running_servers)),
            })

            current_time += time_delta

        # Get current stats
        currently_running = GRPCServerStatus.objects.get_running_servers().count()
        total_servers = (
            GRPCServerStatus.objects.filter(started_at__gte=start_time)
            .values("address")
            .distinct()
            .count()
        )

        return {
            "data_points": data_points,
            "period_hours": hours,
            "granularity": granularity,
            "total_servers": total_servers,
            "currently_running": currently_running,
        }

    @classmethod
    def generate_request_volume_data(cls, hours: int = 24) -> Dict:
        """
        Generate request volume chart data.

        Args:
            hours: Time range in hours

        Returns:
            Dictionary with volume data points and statistics
        """
        start_time, end_time = cls.get_time_range(hours)
        granularity = cls.determine_granularity(hours)

        # Choose truncate function
        trunc_func = TruncHour if granularity == "hour" else TruncDay

        # Aggregate requests by time period
        requests_by_time = (
            GRPCRequestLog.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time,
            )
            .annotate(period=trunc_func("created_at"))
            .values("period")
            .annotate(
                total=Count("id"),
                successful=Count("id", filter=Q(status="success")),
                failed=Count("id", filter=Q(status="error")),
            )
            .order_by("period")
        )

        # Format data points
        data_points = []
        total_requests = 0
        total_success_rate = 0

        for item in requests_by_time:
            total = item["total"]
            successful = item["successful"]
            failed = item["failed"]
            success_rate = (successful / total * 100) if total > 0 else 0

            data_points.append({
                "timestamp": item["period"].isoformat(),
                "total_requests": total,
                "successful_requests": successful,
                "failed_requests": failed,
                "success_rate": round(success_rate, 2),
            })

            total_requests += total
            total_success_rate += success_rate

        avg_success_rate = total_success_rate / len(data_points) if data_points else 0

        return {
            "data_points": data_points,
            "period_hours": hours,
            "granularity": granularity,
            "total_requests": total_requests,
            "avg_success_rate": round(avg_success_rate, 2),
        }

    @classmethod
    def _calculate_percentiles(cls, durations: List[float]) -> Tuple[float, float, float]:
        """Calculate P50, P95, P99 percentiles."""
        if not durations:
            return 0.0, 0.0, 0.0

        sorted_durations = sorted(durations)
        n = len(sorted_durations)

        p50 = sorted_durations[int(n * 0.50)] if n > 0 else 0
        p95 = sorted_durations[int(n * 0.95)] if n > 0 else 0
        p99 = sorted_durations[int(n * 0.99)] if n > 0 else 0

        return float(p50), float(p95), float(p99)

    @classmethod
    def generate_response_time_data(cls, hours: int = 24) -> Dict:
        """
        Generate response time chart data.

        Args:
            hours: Time range in hours

        Returns:
            Dictionary with response time data points and statistics
        """
        start_time, end_time = cls.get_time_range(hours)
        granularity = cls.determine_granularity(hours)

        trunc_func = TruncHour if granularity == "hour" else TruncDay
        time_delta = cls.get_time_delta(granularity)

        # Aggregate response times by period
        times_by_period = (
            GRPCRequestLog.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time,
                duration_ms__isnull=False,
            )
            .annotate(period=trunc_func("created_at"))
            .values("period")
            .annotate(
                avg_duration=Avg("duration_ms"),
                min_duration=Min("duration_ms"),
                max_duration=Max("duration_ms"),
            )
            .order_by("period")
        )

        # Calculate percentiles for each period
        data_points = []
        all_durations = []

        for item in times_by_period:
            period = item["period"]
            period_end = period + time_delta

            # Get all durations for this period
            durations = list(
                GRPCRequestLog.objects.filter(
                    created_at__gte=period,
                    created_at__lt=period_end,
                    duration_ms__isnull=False,
                ).values_list("duration_ms", flat=True)
            )

            all_durations.extend(durations)

            # Calculate percentiles
            p50, p95, p99 = cls._calculate_percentiles(durations)

            data_points.append({
                "timestamp": period.isoformat(),
                "avg_duration_ms": round(item["avg_duration"] or 0, 2),
                "p50_duration_ms": p50,
                "p95_duration_ms": p95,
                "p99_duration_ms": p99,
                "min_duration_ms": float(item["min_duration"] or 0),
                "max_duration_ms": float(item["max_duration"] or 0),
            })

        # Calculate overall stats
        overall_avg = sum(all_durations) / len(all_durations) if all_durations else 0
        _, overall_p95, _ = cls._calculate_percentiles(all_durations)

        return {
            "data_points": data_points,
            "period_hours": hours,
            "granularity": granularity,
            "overall_avg_ms": round(overall_avg, 2),
            "overall_p95_ms": overall_p95,
        }

    @classmethod
    def generate_service_activity_data(cls, hours: int = 24) -> Dict:
        """
        Generate service activity comparison data.

        Args:
            hours: Time range in hours

        Returns:
            Dictionary with service activity data
        """
        start_time, _ = cls.get_time_range(hours)

        # Aggregate by service
        services_stats = (
            GRPCRequestLog.objects.filter(created_at__gte=start_time)
            .values("service_name")
            .annotate(
                request_count=Count("id"),
                successful=Count("id", filter=Q(status="success")),
                avg_duration=Avg("duration_ms"),
            )
            .order_by("-request_count")
        )

        # Format services data
        services = []
        most_active = None
        max_requests = 0

        for item in services_stats:
            request_count = item["request_count"]
            successful = item["successful"]
            success_rate = (successful / request_count * 100) if request_count > 0 else 0

            services.append({
                "service_name": item["service_name"],
                "request_count": request_count,
                "success_rate": round(success_rate, 2),
                "avg_duration_ms": round(item["avg_duration"] or 0, 2),
            })

            if request_count > max_requests:
                max_requests = request_count
                most_active = item["service_name"]

        return {
            "services": services,
            "period_hours": hours,
            "total_services": len(services),
            "most_active_service": most_active,
        }

    @classmethod
    def generate_server_lifecycle_data(cls, hours: int = 24) -> Dict:
        """
        Generate server lifecycle events timeline.

        Args:
            hours: Time range in hours

        Returns:
            Dictionary with lifecycle events
        """
        start_time, _ = cls.get_time_range(hours)

        # Get server events
        servers = GRPCServerStatus.objects.filter(
            started_at__gte=start_time
        ).order_by("started_at")

        events = []
        restart_count = 0
        error_count = 0

        for server in servers:
            # Start event
            events.append({
                "timestamp": server.started_at.isoformat(),
                "event_type": "started",
                "server_address": server.address,
                "server_pid": server.pid,
                "uptime_seconds": None,
                "error_message": None,
            })

            # Stop/Error event
            if server.stopped_at:
                event_type = "error" if server.status == "error" else "stopped"

                if event_type == "error":
                    error_count += 1

                events.append({
                    "timestamp": server.stopped_at.isoformat(),
                    "event_type": event_type,
                    "server_address": server.address,
                    "server_pid": server.pid,
                    "uptime_seconds": server.uptime_seconds,
                    "error_message": server.error_message,
                })

                restart_count += 1

        return {
            "events": events,
            "period_hours": hours,
            "total_events": len(events),
            "restart_count": restart_count,
            "error_count": error_count,
        }

    @classmethod
    def generate_error_distribution_data(cls, hours: int = 24) -> Dict:
        """
        Generate error distribution chart data.

        Args:
            hours: Time range in hours

        Returns:
            Dictionary with error distribution data
        """
        start_time, _ = cls.get_time_range(hours)

        # Get error distribution
        errors = (
            GRPCRequestLog.objects.filter(
                created_at__gte=start_time,
                status="error",
                grpc_status_code__isnull=False,
            )
            .values("grpc_status_code")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        total_errors = sum(item["count"] for item in errors)
        error_types = []
        most_common = None
        max_count = 0

        for item in errors:
            count = item["count"]
            percentage = (count / total_errors * 100) if total_errors > 0 else 0

            error_types.append({
                "error_code": item["grpc_status_code"],
                "count": count,
                "percentage": round(percentage, 2),
                "service_name": None,
            })

            if count > max_count:
                max_count = count
                most_common = item["grpc_status_code"]

        return {
            "error_types": error_types,
            "period_hours": hours,
            "total_errors": total_errors,
            "most_common_error": most_common,
        }

    @classmethod
    def generate_dashboard_data(cls, hours: int = 24) -> Dict:
        """
        Generate all dashboard charts data.

        Args:
            hours: Time range in hours

        Returns:
            Dictionary with all chart data
        """
        return {
            "server_uptime": cls.generate_server_uptime_data(hours),
            "request_volume": cls.generate_request_volume_data(hours),
            "response_time": cls.generate_response_time_data(hours),
            "service_activity": cls.generate_service_activity_data(hours),
            "error_distribution": cls.generate_error_distribution_data(hours),
            "period_hours": hours,
            "generated_at": timezone.now().isoformat(),
        }


__all__ = ["ChartGeneratorService"]
