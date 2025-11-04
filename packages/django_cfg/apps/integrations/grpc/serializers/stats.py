"""
Statistics serializers for gRPC monitoring API.
"""

from rest_framework import serializers


class GRPCRegisteredServiceSerializer(serializers.Serializer):
    """Information about a registered gRPC service."""

    name = serializers.CharField(help_text="Service name")
    full_name = serializers.CharField(help_text="Full service name with package")
    methods_count = serializers.IntegerField(help_text="Number of methods in service")
    request_count = serializers.IntegerField(help_text="Total requests to this service in period")
    error_count = serializers.IntegerField(help_text="Error requests to this service in period")
    success_rate = serializers.FloatField(help_text="Success rate percentage for this service")


class GRPCServerStatusSerializer(serializers.Serializer):
    """gRPC server status and information for overview stats."""

    status = serializers.CharField(help_text="Server status (running, stopped, error, etc.)")
    is_running = serializers.BooleanField(help_text="Whether server is currently running")
    host = serializers.CharField(help_text="Server host address")
    port = serializers.IntegerField(help_text="Server port")
    address = serializers.CharField(help_text="Full server address (host:port)")
    pid = serializers.IntegerField(allow_null=True, help_text="Process ID")
    started_at = serializers.DateTimeField(allow_null=True, help_text="Server start time")
    uptime_seconds = serializers.IntegerField(help_text="Server uptime in seconds")
    uptime_display = serializers.CharField(help_text="Human-readable uptime")
    registered_services_count = serializers.IntegerField(help_text="Number of registered services")
    enable_reflection = serializers.BooleanField(help_text="Whether reflection is enabled")
    enable_health_check = serializers.BooleanField(help_text="Whether health check is enabled")
    last_heartbeat = serializers.DateTimeField(allow_null=True, help_text="Last heartbeat timestamp")
    services = GRPCRegisteredServiceSerializer(many=True, help_text="List of registered services with stats")
    services_healthy = serializers.BooleanField(help_text="Whether all services are healthy (no recent errors)")


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
    server = GRPCServerStatusSerializer(help_text="gRPC server information")


__all__ = [
    "GRPCOverviewStatsSerializer",
    "GRPCServerStatusSerializer",
    "GRPCRegisteredServiceSerializer",
]
