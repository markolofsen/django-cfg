"""
Statistics serializers for Centrifugo monitoring API.
"""

from pydantic import BaseModel, Field


class CentrifugoOverviewStatsSerializer(BaseModel):
    """Overview statistics for Centrifugo publishes."""

    total: int = Field(description="Total publishes in period")
    successful: int = Field(description="Successful publishes")
    failed: int = Field(description="Failed publishes")
    timeout: int = Field(description="Timeout publishes")
    success_rate: float = Field(description="Success rate percentage")
    avg_duration_ms: float = Field(description="Average duration in milliseconds")
    avg_acks_received: float = Field(description="Average ACKs received")
    period_hours: int = Field(description="Statistics period in hours")


__all__ = ["CentrifugoOverviewStatsSerializer"]
