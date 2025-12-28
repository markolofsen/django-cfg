"""
Managers for gRPC Agent Connection State models.

Provides helper methods for:
- Get or create connection state for machine
- Log connection events
- Record metrics
- Query for dashboard visualization
- Calculate uptime statistics

Created: 2025-12-28
Status: Production
"""

from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Any

from django.db import models
from django.db.models import Count, Avg, Sum, F, Q
from django.db.models.functions import TruncHour
from django.utils import timezone


class GrpcAgentConnectionStateQuerySet(models.QuerySet):
    """Custom QuerySet for connection state."""

    def connected(self):
        """Filter connected machines."""
        return self.filter(status="connected")

    def disconnected(self):
        """Filter disconnected machines."""
        return self.filter(status="disconnected")

    def with_errors(self):
        """Filter machines with errors."""
        return self.filter(status="error")

    def healthy(self):
        """Filter healthy connections (connected with good metrics)."""
        return self.filter(
            status="connected",
            consecutive_error_count=0,
        ).filter(
            Q(current_rtt_ms__isnull=True) | Q(current_rtt_ms__lt=1000)
        ).filter(
            Q(current_packet_loss_percent__isnull=True) | Q(current_packet_loss_percent__lt=5)
        )

    def recent(self, hours: int = 24):
        """Filter machines active in last X hours."""
        threshold = timezone.now() - timedelta(hours=hours)
        return self.filter(last_connected_at__gte=threshold)


class GrpcAgentConnectionStateManager(models.Manager):
    """Manager for GrpcAgentConnectionState model."""

    def get_queryset(self):
        return GrpcAgentConnectionStateQuerySet(self.model, using=self._db)

    def connected(self):
        return self.get_queryset().connected()

    def healthy(self):
        return self.get_queryset().healthy()

    def get_or_create_for_machine(
        self,
        machine_id: str,
        machine_name: str,
    ) -> Tuple[Any, bool]:
        """
        Get or create connection state for a machine.

        Args:
            machine_id: Unique machine identifier
            machine_name: Human-readable machine name

        Returns:
            Tuple of (connection_state, created)
        """
        return self.get_or_create(
            machine_id=machine_id,
            defaults={
                "machine_name": machine_name,
            }
        )

    def get_summary_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get summary statistics for dashboard.

        Args:
            hours: Hours to look back for recent activity

        Returns:
            Dictionary with summary stats
        """
        qs = self.get_queryset()
        recent_qs = qs.recent(hours=hours)

        total = qs.count()
        connected = qs.connected().count()
        disconnected = qs.disconnected().count()
        errors = qs.with_errors().count()

        # Calculate connectivity percentage
        connectivity_pct = (connected / total * 100) if total > 0 else 0.0

        # Count recent errors
        recent_errors = recent_qs.filter(
            consecutive_error_count__gt=0
        ).count()

        return {
            "total_machines": total,
            "connected": connected,
            "disconnected": disconnected,
            "errors": errors,
            "connectivity_percentage": round(connectivity_pct, 2),
            "recent_errors": recent_errors,
            "period_hours": hours,
        }

    def get_uptime_stats(self, machine_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Calculate uptime statistics for a machine.

        Args:
            machine_id: Machine identifier
            days: Number of days to analyze

        Returns:
            Dictionary with uptime stats
        """
        from ..models import GrpcAgentConnectionEvent

        threshold = timezone.now() - timedelta(days=days)
        total_seconds = days * 24 * 60 * 60

        try:
            state = self.get(machine_id=machine_id)
        except self.model.DoesNotExist:
            return {
                "total_seconds": total_seconds,
                "uptime_seconds": 0,
                "downtime_seconds": total_seconds,
                "uptime_percentage": 0.0,
                "period_days": days,
            }

        # Get all events in period
        events = GrpcAgentConnectionEvent.objects.filter(
            connection_state=state,
            timestamp__gte=threshold,
        ).order_by("timestamp")

        # Calculate uptime by summing connected periods
        uptime_seconds = 0
        last_connect_time = None

        for event in events:
            if event.event_type == "connected":
                last_connect_time = event.timestamp
            elif event.event_type == "disconnected" and last_connect_time:
                uptime_seconds += (event.timestamp - last_connect_time).total_seconds()
                last_connect_time = None

        # If still connected, add time until now
        if last_connect_time and state.status == "connected":
            uptime_seconds += (timezone.now() - last_connect_time).total_seconds()

        downtime_seconds = total_seconds - uptime_seconds
        uptime_pct = (uptime_seconds / total_seconds * 100) if total_seconds > 0 else 0.0

        return {
            "total_seconds": total_seconds,
            "uptime_seconds": int(uptime_seconds),
            "downtime_seconds": int(downtime_seconds),
            "uptime_percentage": round(uptime_pct, 2),
            "period_days": days,
        }


class GrpcAgentConnectionEventManager(models.Manager):
    """Manager for GrpcAgentConnectionEvent model."""

    def log_connection(
        self,
        connection_state,
        ip_address: str = None,
        client_version: str = None,
    ):
        """
        Log a connection event.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            ip_address: Client IP address
            client_version: Client version string

        Returns:
            Created event
        """
        return self.create(
            connection_state=connection_state,
            event_type="connected",
            ip_address=ip_address,
            client_version=client_version or "",
        )

    def log_disconnection(
        self,
        connection_state,
        duration_seconds: int = None,
    ):
        """
        Log a disconnection event.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            duration_seconds: How long the connection was active

        Returns:
            Created event
        """
        return self.create(
            connection_state=connection_state,
            event_type="disconnected",
            duration_seconds=duration_seconds,
        )

    def log_error(
        self,
        connection_state,
        error_message: str,
        error_code: str = "",
        error_details: dict = None,
    ):
        """
        Log an error event.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            error_message: Error message
            error_code: Error code (e.g., gRPC status code name)
            error_details: Additional details as dict

        Returns:
            Created event
        """
        return self.create(
            connection_state=connection_state,
            event_type="error",
            error_message=error_message,
            error_code=error_code,
            error_details=error_details,
        )

    def get_timeline(
        self,
        machine_id: str,
        hours: int = 24,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get event timeline for a machine.

        Args:
            machine_id: Machine identifier
            hours: Hours to look back
            limit: Maximum events to return

        Returns:
            List of event dictionaries
        """
        threshold = timezone.now() - timedelta(hours=hours)

        events = self.filter(
            connection_state__machine_id=machine_id,
            timestamp__gte=threshold,
        ).order_by("-timestamp")[:limit]

        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "error_message": e.error_message or None,
                "duration_seconds": e.duration_seconds,
            }
            for e in events
        ]


class GrpcAgentConnectionMetricManager(models.Manager):
    """Manager for GrpcAgentConnectionMetric model."""

    def record_metrics(
        self,
        connection_state,
        **metrics,
    ):
        """
        Record metrics sample.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            **metrics: Metric values (rtt_min_ms, rtt_max_ms, etc.)

        Returns:
            Created metric record
        """
        # Filter to only valid metric fields
        valid_fields = {
            "rtt_min_ms", "rtt_max_ms", "rtt_mean_ms", "rtt_stddev_ms",
            "packet_loss_percent", "packets_sent", "packets_received",
            "keepalive_sent", "keepalive_ack", "keepalive_timeout",
            "active_streams", "failed_streams", "sample_window_seconds",
        }
        filtered_metrics = {k: v for k, v in metrics.items() if k in valid_fields}

        return self.create(
            connection_state=connection_state,
            **filtered_metrics,
        )

    def get_quality_trends(
        self,
        machine_id: str,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Get quality trend data for a machine.

        Args:
            machine_id: Machine identifier
            hours: Hours to analyze

        Returns:
            Dictionary with trend data
        """
        threshold = timezone.now() - timedelta(hours=hours)

        metrics = self.filter(
            connection_state__machine_id=machine_id,
            timestamp__gte=threshold,
        )

        # Aggregate metrics
        agg = metrics.aggregate(
            avg_rtt=Avg("rtt_mean_ms"),
            avg_packet_loss=Avg("packet_loss_percent"),
            total_keepalive_sent=Sum("keepalive_sent"),
            total_keepalive_timeout=Sum("keepalive_timeout"),
            total_failed_streams=Sum("failed_streams"),
        )

        # Health status distribution
        health_counts = metrics.values("health_status").annotate(
            count=Count("id")
        )

        return {
            "period_hours": hours,
            "avg_rtt_ms": round(agg["avg_rtt"] or 0, 2),
            "avg_packet_loss_percent": round(agg["avg_packet_loss"] or 0, 2),
            "keepalive_timeout_rate": (
                (agg["total_keepalive_timeout"] or 0) /
                (agg["total_keepalive_sent"] or 1)
            ),
            "total_failed_streams": agg["total_failed_streams"] or 0,
            "health_distribution": {
                h["health_status"]: h["count"]
                for h in health_counts
            },
        }

    def get_graph_data(
        self,
        machine_id: str,
        hours: int = 24,
        resolution_seconds: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get time-series data for graph visualization.

        Args:
            machine_id: Machine identifier
            hours: Hours to fetch
            resolution_seconds: Approximate seconds between points

        Returns:
            List of data points for graphing
        """
        threshold = timezone.now() - timedelta(hours=hours)

        metrics = self.filter(
            connection_state__machine_id=machine_id,
            timestamp__gte=threshold,
        ).order_by("timestamp").values(
            "timestamp",
            "rtt_mean_ms",
            "packet_loss_percent",
            "health_status",
        )

        return [
            {
                "timestamp": m["timestamp"].isoformat(),
                "avg_rtt_ms": m["rtt_mean_ms"],
                "avg_packet_loss_percent": m["packet_loss_percent"],
                "health_status": m["health_status"],
            }
            for m in metrics
        ]
