"""
Statistics serializers for gRPC monitoring API.
"""

from pydantic import BaseModel, Field


class GRPCOverviewStatsSerializer(BaseModel):
    """Overview statistics for gRPC requests."""

    total: int = Field(description="Total requests in period")
    successful: int = Field(description="Successful requests")
    errors: int = Field(description="Error requests")
    cancelled: int = Field(description="Cancelled requests")
    timeout: int = Field(description="Timeout requests")
    success_rate: float = Field(description="Success rate percentage")
    avg_duration_ms: float = Field(description="Average duration in milliseconds")
    p95_duration_ms: float = Field(description="95th percentile duration in milliseconds")
    period_hours: int = Field(description="Statistics period in hours")


__all__ = ["GRPCOverviewStatsSerializer"]
