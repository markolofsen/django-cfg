from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthCheck(BaseModel):
    """
    Health check response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    status: str = Field(description='Health status: healthy or unhealthy')
    wrapper_url: str = Field(description='Configured wrapper URL')
    has_api_key: bool = Field(description='Whether API key is configured')
    timestamp: str = Field(description='Current timestamp')



class OverviewStats(BaseModel):
    """
    Overview statistics for Centrifugo publishes.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    total: int = Field(description='Total publishes in period')
    successful: int = Field(description='Successful publishes')
    failed: int = Field(description='Failed publishes')
    timeout: int = Field(description='Timeout publishes')
    success_rate: float = Field(description='Success rate percentage')
    avg_duration_ms: float = Field(description='Average duration in milliseconds')
    avg_acks_received: float = Field(description='Average ACKs received')
    period_hours: int = Field(description='Statistics period in hours')



class RecentPublishes(BaseModel):
    """
    Recent publishes list.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    publishes: list[Any] = Field(description='List of recent publishes')
    count: int = Field(description='Number of publishes returned')
    total_available: int = Field(description='Total publishes available')
    offset: int = Field(None, description='Current offset for pagination')
    has_more: bool = Field(None, description='Whether more results are available')



class ChannelList(BaseModel):
    """
    List of channel statistics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    channels: list[Any] = Field(description='Channel statistics')
    total_channels: int = Field(description='Total number of channels')



