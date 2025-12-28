"""
Manager for GrpcAgentConnectionMetric model.

Provides:
- Record metrics samples
- Query trends and graph data
- Aggregate statistics

Created: 2025-12-28
Refactored: 2025-12-29
"""

from datetime import timedelta
from typing import Any, Dict, List

from django.db import models
from django.db.models import Avg, Count, Sum
from django.utils import timezone


# Valid metric fields for validation
VALID_METRIC_FIELDS = frozenset({
    "rtt_min_ms", "rtt_max_ms", "rtt_mean_ms", "rtt_stddev_ms",
    "packet_loss_percent", "packets_sent", "packets_received",
    "keepalive_sent", "keepalive_ack", "keepalive_timeout",
    "active_streams", "failed_streams", "sample_window_seconds",
})


class GrpcAgentConnectionMetricManager(models.Manager):
    """Manager for GrpcAgentConnectionMetric model."""

    # =========================================================================
    # Recording metrics
    # =========================================================================

    def record_metrics(self, connection_state, **metrics):
        """
        Record metrics sample.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            **metrics: Metric values (rtt_min_ms, rtt_max_ms, etc.)

        Returns:
            Created metric record
        """
        filtered_metrics = {
            k: v for k, v in metrics.items()
            if k in VALID_METRIC_FIELDS
        }

        return self.create(
            connection_state=connection_state,
            **filtered_metrics,
        )

    async def arecord_metrics(self, connection_state, **metrics):
        """Record metrics sample (ASYNC)."""
        filtered_metrics = {
            k: v for k, v in metrics.items()
            if k in VALID_METRIC_FIELDS
        }

        return await self.acreate(
            connection_state=connection_state,
            **filtered_metrics,
        )

    # =========================================================================
    # Queries
    # =========================================================================

    def for_machine(self, machine_id: str):
        """Filter metrics for a specific machine."""
        return self.filter(connection_state__machine_id=machine_id)

    def recent(self, hours: int = 24):
        """Filter recent metrics."""
        threshold = timezone.now() - timedelta(hours=hours)
        return self.filter(timestamp__gte=threshold)

    def healthy_only(self):
        """Filter healthy status metrics only."""
        return self.filter(health_status="healthy")

    def degraded_only(self):
        """Filter degraded status metrics only."""
        return self.filter(health_status="degraded")

    def poor_only(self):
        """Filter poor status metrics only."""
        return self.filter(health_status="poor")

    # =========================================================================
    # Analytics
    # =========================================================================

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

        agg = metrics.aggregate(
            avg_rtt=Avg("rtt_mean_ms"),
            avg_packet_loss=Avg("packet_loss_percent"),
            total_keepalive_sent=Sum("keepalive_sent"),
            total_keepalive_timeout=Sum("keepalive_timeout"),
            total_failed_streams=Sum("failed_streams"),
        )

        health_counts = metrics.values("health_status").annotate(
            count=Count("id")
        )

        keepalive_sent = agg["total_keepalive_sent"] or 1
        keepalive_timeout = agg["total_keepalive_timeout"] or 0

        return {
            "period_hours": hours,
            "avg_rtt_ms": round(agg["avg_rtt"] or 0, 2),
            "avg_packet_loss_percent": round(agg["avg_packet_loss"] or 0, 2),
            "keepalive_timeout_rate": keepalive_timeout / keepalive_sent,
            "total_failed_streams": agg["total_failed_streams"] or 0,
            "health_distribution": {
                h["health_status"]: h["count"]
                for h in health_counts
            },
        }

    async def aget_quality_trends(
        self,
        machine_id: str,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """Get quality trend data for a machine (ASYNC)."""
        from asgiref.sync import sync_to_async
        return await sync_to_async(self.get_quality_trends)(machine_id, hours)

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

    async def aget_graph_data(
        self,
        machine_id: str,
        hours: int = 24,
        resolution_seconds: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get time-series data for graph visualization (ASYNC)."""
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

        result = []
        async for m in metrics:
            result.append({
                "timestamp": m["timestamp"].isoformat(),
                "avg_rtt_ms": m["rtt_mean_ms"],
                "avg_packet_loss_percent": m["packet_loss_percent"],
                "health_status": m["health_status"],
            })
        return result

    def get_latest_for_machine(self, machine_id: str):
        """Get the latest metric for a machine."""
        return self.filter(
            connection_state__machine_id=machine_id
        ).order_by("-timestamp").first()

    async def aget_latest_for_machine(self, machine_id: str):
        """Get the latest metric for a machine (ASYNC)."""
        return await self.filter(
            connection_state__machine_id=machine_id
        ).order_by("-timestamp").afirst()
