"""
DRF serializers for gRPC charts and statistics data.

These serializers define the structure for chart endpoints
that provide time-series data for visualization.
"""

from rest_framework import serializers


class TimeSeriesDataPoint(serializers.Serializer):
    """Single data point in time series."""

    timestamp = serializers.CharField(help_text="ISO timestamp")
    value = serializers.FloatField(help_text="Value at this timestamp")
    label = serializers.CharField(
        required=False, allow_null=True, help_text="Optional label for this point"
    )


class ServerUptimeDataPoint(serializers.Serializer):
    """Server uptime data point."""

    timestamp = serializers.CharField(help_text="ISO timestamp")
    server_count = serializers.IntegerField(help_text="Number of running servers")
    servers = serializers.ListField(
        child=serializers.CharField(), default=list, help_text="List of server addresses"
    )


class RequestVolumeDataPoint(serializers.Serializer):
    """Request volume data point."""

    timestamp = serializers.CharField(help_text="ISO timestamp")
    total_requests = serializers.IntegerField(help_text="Total requests in period")
    successful_requests = serializers.IntegerField(help_text="Successful requests")
    failed_requests = serializers.IntegerField(help_text="Failed requests")
    success_rate = serializers.FloatField(help_text="Success rate percentage")


class ResponseTimeDataPoint(serializers.Serializer):
    """Response time statistics data point."""

    timestamp = serializers.CharField(help_text="ISO timestamp")
    avg_duration_ms = serializers.FloatField(help_text="Average duration")
    p50_duration_ms = serializers.FloatField(help_text="P50 percentile")
    p95_duration_ms = serializers.FloatField(help_text="P95 percentile")
    p99_duration_ms = serializers.FloatField(help_text="P99 percentile")
    min_duration_ms = serializers.FloatField(help_text="Minimum duration")
    max_duration_ms = serializers.FloatField(help_text="Maximum duration")


class ServiceActivityDataPoint(serializers.Serializer):
    """Service activity data point."""

    service_name = serializers.CharField(help_text="Service name")
    request_count = serializers.IntegerField(help_text="Number of requests")
    success_rate = serializers.FloatField(help_text="Success rate percentage")
    avg_duration_ms = serializers.FloatField(help_text="Average duration")


class ServerLifecycleEvent(serializers.Serializer):
    """Server lifecycle event."""

    timestamp = serializers.CharField(help_text="Event timestamp")
    event_type = serializers.CharField(
        help_text="Event type (started, stopped, error)"
    )
    server_address = serializers.CharField(help_text="Server address")
    server_pid = serializers.IntegerField(help_text="Server process ID")
    uptime_seconds = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Uptime at event time (for stop events)",
    )
    error_message = serializers.CharField(
        required=False, allow_null=True, help_text="Error message if applicable"
    )


class TimeSeriesChartData(serializers.Serializer):
    """Generic time series chart data."""

    title = serializers.CharField(help_text="Chart title")
    series_name = serializers.CharField(help_text="Series name")
    data_points = TimeSeriesDataPoint(many=True, default=list, help_text="Data points")
    period_hours = serializers.IntegerField(help_text="Period in hours")
    granularity = serializers.CharField(help_text="Data granularity (hour, day, week)")


class ServerUptimeChartSerializer(serializers.Serializer):
    """Server uptime over time chart data."""

    title = serializers.CharField(default="Server Uptime", help_text="Chart title")
    data_points = ServerUptimeDataPoint(
        many=True, default=list, help_text="Uptime data points"
    )
    period_hours = serializers.IntegerField(help_text="Period in hours")
    granularity = serializers.CharField(help_text="Data granularity")
    total_servers = serializers.IntegerField(
        help_text="Total unique servers in period"
    )
    currently_running = serializers.IntegerField(help_text="Currently running servers")


class RequestVolumeChartSerializer(serializers.Serializer):
    """Request volume over time chart data."""

    title = serializers.CharField(default="Request Volume", help_text="Chart title")
    data_points = RequestVolumeDataPoint(
        many=True, default=list, help_text="Volume data points"
    )
    period_hours = serializers.IntegerField(help_text="Period in hours")
    granularity = serializers.CharField(help_text="Data granularity")
    total_requests = serializers.IntegerField(help_text="Total requests in period")
    avg_success_rate = serializers.FloatField(help_text="Average success rate")


class ResponseTimeChartSerializer(serializers.Serializer):
    """Response time over time chart data."""

    title = serializers.CharField(default="Response Time", help_text="Chart title")
    data_points = ResponseTimeDataPoint(
        many=True, default=list, help_text="Response time data points"
    )
    period_hours = serializers.IntegerField(help_text="Period in hours")
    granularity = serializers.CharField(help_text="Data granularity")
    overall_avg_ms = serializers.FloatField(help_text="Overall average duration")
    overall_p95_ms = serializers.FloatField(help_text="Overall P95 duration")


class ServiceActivityChartSerializer(serializers.Serializer):
    """Service activity comparison chart data."""

    title = serializers.CharField(default="Service Activity", help_text="Chart title")
    services = ServiceActivityDataPoint(
        many=True, default=list, help_text="Service activity data"
    )
    period_hours = serializers.IntegerField(help_text="Period in hours")
    total_services = serializers.IntegerField(help_text="Total number of services")
    most_active_service = serializers.CharField(
        required=False, allow_null=True, help_text="Most active service name"
    )


class ServerLifecycleChartSerializer(serializers.Serializer):
    """Server lifecycle events timeline."""

    title = serializers.CharField(default="Server Lifecycle", help_text="Chart title")
    events = ServerLifecycleEvent(
        many=True, default=list, help_text="Lifecycle events"
    )
    period_hours = serializers.IntegerField(help_text="Period in hours")
    total_events = serializers.IntegerField(help_text="Total number of events")
    restart_count = serializers.IntegerField(help_text="Number of server restarts")
    error_count = serializers.IntegerField(help_text="Number of error events")


class ErrorDistributionDataPoint(serializers.Serializer):
    """Error distribution data point."""

    error_code = serializers.CharField(help_text="gRPC status code")
    count = serializers.IntegerField(help_text="Number of occurrences")
    percentage = serializers.FloatField(help_text="Percentage of total errors")
    service_name = serializers.CharField(
        required=False, allow_null=True, help_text="Service name if filtered"
    )


class ErrorDistributionChartSerializer(serializers.Serializer):
    """Error distribution chart data."""

    title = serializers.CharField(default="Error Distribution", help_text="Chart title")
    error_types = ErrorDistributionDataPoint(
        many=True, default=list, help_text="Error distribution data"
    )
    period_hours = serializers.IntegerField(help_text="Period in hours")
    total_errors = serializers.IntegerField(help_text="Total number of errors")
    most_common_error = serializers.CharField(
        required=False, allow_null=True, help_text="Most common error code"
    )


class DashboardChartsSerializer(serializers.Serializer):
    """Combined dashboard charts data."""

    server_uptime = ServerUptimeChartSerializer(help_text="Server uptime chart")
    request_volume = RequestVolumeChartSerializer(help_text="Request volume chart")
    response_time = ResponseTimeChartSerializer(help_text="Response time chart")
    service_activity = ServiceActivityChartSerializer(help_text="Service activity chart")
    error_distribution = ErrorDistributionChartSerializer(
        help_text="Error distribution chart"
    )
    period_hours = serializers.IntegerField(
        help_text="Period in hours for all charts"
    )
    generated_at = serializers.CharField(help_text="When data was generated")


__all__ = [
    "TimeSeriesDataPoint",
    "ServerUptimeDataPoint",
    "RequestVolumeDataPoint",
    "ResponseTimeDataPoint",
    "ServiceActivityDataPoint",
    "ServerLifecycleEvent",
    "TimeSeriesChartData",
    "ServerUptimeChartSerializer",
    "RequestVolumeChartSerializer",
    "ResponseTimeChartSerializer",
    "ServiceActivityChartSerializer",
    "ServerLifecycleChartSerializer",
    "ErrorDistributionDataPoint",
    "ErrorDistributionChartSerializer",
    "DashboardChartsSerializer",
]
