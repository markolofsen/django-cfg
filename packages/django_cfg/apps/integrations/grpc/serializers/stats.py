"""
Statistics serializers for gRPC monitoring API.
"""

from rest_framework import serializers


class GRPCOverviewStatsSerializer(serializers.Serializer):
    """Overview statistics for gRPC requests."""

    total = serializers.IntegerField(help_text="Total requests in period")
    successful = serializers.IntegerField(help_text="Successful requests")
    errors = serializers.IntegerField(help_text="Error requests")
    cancelled = serializers.IntegerField(help_text="Cancelled requests")
    timeout = serializers.IntegerField(help_text="Timeout requests")
    success_rate = serializers.FloatField(help_text="Success rate percentage")
    avg_duration_ms = serializers.FloatField(help_text="Average duration in milliseconds")
    p95_duration_ms = serializers.FloatField(
        allow_null=True, help_text="95th percentile duration in milliseconds"
    )
    period_hours = serializers.IntegerField(help_text="Statistics period in hours")


__all__ = ["GRPCOverviewStatsSerializer"]
