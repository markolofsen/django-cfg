"""
Pydantic serializers for gRPC charts and statistics data.

These serializers define the structure for chart endpoints
that provide time-series data for visualization.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series."""

    timestamp: str = Field(..., description="ISO timestamp")
    value: float = Field(..., description="Value at this timestamp")
    label: Optional[str] = Field(None, description="Optional label for this point")


class ServerUptimeDataPoint(BaseModel):
    """Server uptime data point."""

    timestamp: str = Field(..., description="ISO timestamp")
    server_count: int = Field(..., description="Number of running servers")
    servers: List[str] = Field(
        default_factory=list, description="List of server addresses"
    )


class RequestVolumeDataPoint(BaseModel):
    """Request volume data point."""

    timestamp: str = Field(..., description="ISO timestamp")
    total_requests: int = Field(..., description="Total requests in period")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    success_rate: float = Field(..., description="Success rate percentage")


class ResponseTimeDataPoint(BaseModel):
    """Response time statistics data point."""

    timestamp: str = Field(..., description="ISO timestamp")
    avg_duration_ms: float = Field(..., description="Average duration")
    p50_duration_ms: float = Field(..., description="P50 percentile")
    p95_duration_ms: float = Field(..., description="P95 percentile")
    p99_duration_ms: float = Field(..., description="P99 percentile")
    min_duration_ms: float = Field(..., description="Minimum duration")
    max_duration_ms: float = Field(..., description="Maximum duration")


class ServiceActivityDataPoint(BaseModel):
    """Service activity data point."""

    service_name: str = Field(..., description="Service name")
    request_count: int = Field(..., description="Number of requests")
    success_rate: float = Field(..., description="Success rate percentage")
    avg_duration_ms: float = Field(..., description="Average duration")


class ServerLifecycleEvent(BaseModel):
    """Server lifecycle event."""

    timestamp: str = Field(..., description="Event timestamp")
    event_type: str = Field(
        ..., description="Event type (started, stopped, error)"
    )
    server_address: str = Field(..., description="Server address")
    server_pid: int = Field(..., description="Server process ID")
    uptime_seconds: Optional[int] = Field(
        None, description="Uptime at event time (for stop events)"
    )
    error_message: Optional[str] = Field(None, description="Error message if applicable")


class TimeSeriesChartData(BaseModel):
    """Generic time series chart data."""

    title: str = Field(..., description="Chart title")
    series_name: str = Field(..., description="Series name")
    data_points: List[TimeSeriesDataPoint] = Field(
        default_factory=list, description="Data points"
    )
    period_hours: int = Field(..., description="Period in hours")
    granularity: str = Field(
        ..., description="Data granularity (hour, day, week)"
    )


class ServerUptimeChartSerializer(BaseModel):
    """Server uptime over time chart data."""

    title: str = Field(default="Server Uptime", description="Chart title")
    data_points: List[ServerUptimeDataPoint] = Field(
        default_factory=list, description="Uptime data points"
    )
    period_hours: int = Field(..., description="Period in hours")
    granularity: str = Field(..., description="Data granularity")
    total_servers: int = Field(..., description="Total unique servers in period")
    currently_running: int = Field(..., description="Currently running servers")


class RequestVolumeChartSerializer(BaseModel):
    """Request volume over time chart data."""

    title: str = Field(default="Request Volume", description="Chart title")
    data_points: List[RequestVolumeDataPoint] = Field(
        default_factory=list, description="Volume data points"
    )
    period_hours: int = Field(..., description="Period in hours")
    granularity: str = Field(..., description="Data granularity")
    total_requests: int = Field(..., description="Total requests in period")
    avg_success_rate: float = Field(..., description="Average success rate")


class ResponseTimeChartSerializer(BaseModel):
    """Response time over time chart data."""

    title: str = Field(default="Response Time", description="Chart title")
    data_points: List[ResponseTimeDataPoint] = Field(
        default_factory=list, description="Response time data points"
    )
    period_hours: int = Field(..., description="Period in hours")
    granularity: str = Field(..., description="Data granularity")
    overall_avg_ms: float = Field(..., description="Overall average duration")
    overall_p95_ms: float = Field(..., description="Overall P95 duration")


class ServiceActivityChartSerializer(BaseModel):
    """Service activity comparison chart data."""

    title: str = Field(default="Service Activity", description="Chart title")
    services: List[ServiceActivityDataPoint] = Field(
        default_factory=list, description="Service activity data"
    )
    period_hours: int = Field(..., description="Period in hours")
    total_services: int = Field(..., description="Total number of services")
    most_active_service: Optional[str] = Field(
        None, description="Most active service name"
    )


class ServerLifecycleChartSerializer(BaseModel):
    """Server lifecycle events timeline."""

    title: str = Field(default="Server Lifecycle", description="Chart title")
    events: List[ServerLifecycleEvent] = Field(
        default_factory=list, description="Lifecycle events"
    )
    period_hours: int = Field(..., description="Period in hours")
    total_events: int = Field(..., description="Total number of events")
    restart_count: int = Field(..., description="Number of server restarts")
    error_count: int = Field(..., description="Number of error events")


class ErrorDistributionDataPoint(BaseModel):
    """Error distribution data point."""

    error_code: str = Field(..., description="gRPC status code")
    count: int = Field(..., description="Number of occurrences")
    percentage: float = Field(..., description="Percentage of total errors")
    service_name: Optional[str] = Field(None, description="Service name if filtered")


class ErrorDistributionChartSerializer(BaseModel):
    """Error distribution chart data."""

    title: str = Field(default="Error Distribution", description="Chart title")
    error_types: List[ErrorDistributionDataPoint] = Field(
        default_factory=list, description="Error distribution data"
    )
    period_hours: int = Field(..., description="Period in hours")
    total_errors: int = Field(..., description="Total number of errors")
    most_common_error: Optional[str] = Field(
        None, description="Most common error code"
    )


class DashboardChartsSerializer(BaseModel):
    """Combined dashboard charts data."""

    server_uptime: ServerUptimeChartSerializer = Field(
        ..., description="Server uptime chart"
    )
    request_volume: RequestVolumeChartSerializer = Field(
        ..., description="Request volume chart"
    )
    response_time: ResponseTimeChartSerializer = Field(
        ..., description="Response time chart"
    )
    service_activity: ServiceActivityChartSerializer = Field(
        ..., description="Service activity chart"
    )
    error_distribution: ErrorDistributionChartSerializer = Field(
        ..., description="Error distribution chart"
    )
    period_hours: int = Field(..., description="Period in hours for all charts")
    generated_at: str = Field(..., description="When data was generated")


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
