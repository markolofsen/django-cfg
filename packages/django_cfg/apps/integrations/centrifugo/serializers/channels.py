"""
Channel statistics serializers for Centrifugo monitoring API.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChannelStatsSerializer(BaseModel):
    """Statistics per channel."""

    channel: str = Field(description="Channel name")
    total: int = Field(description="Total publishes to this channel")
    successful: int = Field(description="Successful publishes")
    failed: int = Field(description="Failed publishes")
    avg_duration_ms: float = Field(description="Average duration")
    avg_acks: float = Field(description="Average ACKs received")
    last_activity_at: Optional[str] = Field(default=None, description="Last activity timestamp (ISO format)")


class ChannelListSerializer(BaseModel):
    """List of channel statistics."""

    channels: list[ChannelStatsSerializer] = Field(description="Channel statistics")
    total_channels: int = Field(description="Total number of channels")


__all__ = ["ChannelStatsSerializer", "ChannelListSerializer"]
