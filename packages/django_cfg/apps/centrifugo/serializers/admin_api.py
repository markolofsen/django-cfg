"""
Centrifugo Admin API Serializers.

Pydantic models for Centrifugo server HTTP API requests and responses.
Based on Centrifugo v6 API specification from api.proto.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==================== Common Types ====================


class CentrifugoError(BaseModel):
    """Centrifugo API error structure."""

    code: int = Field(default=0, description="Error code (0 = no error)")
    message: str = Field(default="", description="Error message")


class CentrifugoMetrics(BaseModel):
    """Server metrics."""

    interval: float = Field(description="Metrics collection interval")
    items: Dict[str, float] = Field(description="Metric name to value mapping")


class CentrifugoProcess(BaseModel):
    """Process information."""

    cpu: float = Field(description="CPU usage percentage")
    rss: int = Field(description="Resident set size in bytes")


# ==================== Info API ====================


class CentrifugoInfoRequest(BaseModel):
    """Request for server info (no parameters)."""

    pass


class CentrifugoNodeInfo(BaseModel):
    """Information about a single Centrifugo node."""

    uid: str = Field(description="Unique node identifier")
    name: str = Field(description="Node name")
    version: str = Field(description="Centrifugo version")
    num_clients: int = Field(description="Number of connected clients")
    num_users: int = Field(description="Number of unique users")
    num_channels: int = Field(description="Number of active channels")
    uptime: int = Field(description="Node uptime in seconds")
    num_subs: int = Field(description="Total number of subscriptions")
    metrics: Optional[CentrifugoMetrics] = Field(
        default=None, description="Server metrics"
    )
    process: Optional[CentrifugoProcess] = Field(
        default=None, description="Process information"
    )


class CentrifugoInfoResult(BaseModel):
    """Info result wrapper."""

    nodes: List[CentrifugoNodeInfo] = Field(description="List of Centrifugo nodes")


class CentrifugoInfoResponse(BaseModel):
    """Server info response."""

    error: Optional[CentrifugoError] = Field(default=None, description="Error if any")
    result: Optional[CentrifugoInfoResult] = Field(
        default=None, description="Result data"
    )


# ==================== Channels API ====================


class CentrifugoChannelsRequest(BaseModel):
    """Request to list active channels."""

    pattern: Optional[str] = Field(
        default=None, description="Pattern to filter channels (e.g., 'user:*')"
    )


class CentrifugoChannelInfo(BaseModel):
    """Information about a single channel."""

    num_clients: int = Field(description="Number of connected clients in channel")


class CentrifugoChannelsResult(BaseModel):
    """Channels result wrapper."""

    channels: Dict[str, CentrifugoChannelInfo] = Field(
        description="Map of channel names to channel info"
    )


class CentrifugoChannelsResponse(BaseModel):
    """List of active channels response."""

    error: Optional[CentrifugoError] = Field(default=None, description="Error if any")
    result: Optional[CentrifugoChannelsResult] = Field(
        default=None, description="Result data"
    )


# ==================== Presence API ====================


class CentrifugoPresenceRequest(BaseModel):
    """Request to get channel presence."""

    channel: str = Field(description="Channel name")


class CentrifugoClientInfo(BaseModel):
    """Information about connected client."""

    user: str = Field(description="User ID")
    client: str = Field(description="Client UUID")
    conn_info: Optional[Dict[str, Any]] = Field(
        default=None, description="Connection metadata"
    )
    chan_info: Optional[Dict[str, Any]] = Field(
        default=None, description="Channel-specific metadata"
    )


class CentrifugoPresenceResult(BaseModel):
    """Presence result wrapper."""

    presence: Dict[str, CentrifugoClientInfo] = Field(
        description="Map of client IDs to client info"
    )


class CentrifugoPresenceResponse(BaseModel):
    """Channel presence response."""

    error: Optional[CentrifugoError] = Field(default=None, description="Error if any")
    result: Optional[CentrifugoPresenceResult] = Field(
        default=None, description="Result data"
    )


# ==================== Presence Stats API ====================


class CentrifugoPresenceStatsRequest(BaseModel):
    """Request to get channel presence statistics."""

    channel: str = Field(description="Channel name")


class CentrifugoPresenceStatsResult(BaseModel):
    """Presence stats result."""

    num_clients: int = Field(description="Number of connected clients")
    num_users: int = Field(description="Number of unique users")


class CentrifugoPresenceStatsResponse(BaseModel):
    """Channel presence stats response."""

    error: Optional[CentrifugoError] = Field(default=None, description="Error if any")
    result: Optional[CentrifugoPresenceStatsResult] = Field(
        default=None, description="Result data"
    )


# ==================== History API ====================


class CentrifugoStreamPosition(BaseModel):
    """Stream position for pagination."""

    offset: int = Field(description="Stream offset")
    epoch: str = Field(description="Stream epoch")


class CentrifugoHistoryRequest(BaseModel):
    """Request to get channel history."""

    channel: str = Field(description="Channel name")
    limit: Optional[int] = Field(
        default=None, ge=1, le=1000, description="Maximum number of messages to return"
    )
    since: Optional[CentrifugoStreamPosition] = Field(
        default=None, description="Stream position to get messages since"
    )
    reverse: Optional[bool] = Field(
        default=False, description="Reverse message order (newest first)"
    )


class CentrifugoPublication(BaseModel):
    """Single publication (message) in channel history."""

    data: Dict[str, Any] = Field(description="Message payload")
    info: Optional[CentrifugoClientInfo] = Field(
        default=None, description="Publisher client info"
    )
    offset: int = Field(description="Message offset in channel stream")
    tags: Optional[Dict[str, str]] = Field(
        default=None, description="Optional message tags"
    )


class CentrifugoHistoryResult(BaseModel):
    """History result wrapper."""

    publications: List[CentrifugoPublication] = Field(
        description="List of publications"
    )
    epoch: str = Field(description="Current stream epoch")
    offset: int = Field(description="Latest stream offset")


class CentrifugoHistoryResponse(BaseModel):
    """Channel history response."""

    error: Optional[CentrifugoError] = Field(default=None, description="Error if any")
    result: Optional[CentrifugoHistoryResult] = Field(
        default=None, description="Result data"
    )


__all__ = [
    # Common types
    "CentrifugoError",
    "CentrifugoMetrics",
    "CentrifugoProcess",
    # Info API
    "CentrifugoInfoRequest",
    "CentrifugoInfoResponse",
    "CentrifugoInfoResult",
    "CentrifugoNodeInfo",
    # Channels API
    "CentrifugoChannelsRequest",
    "CentrifugoChannelsResponse",
    "CentrifugoChannelsResult",
    "CentrifugoChannelInfo",
    # Presence API
    "CentrifugoPresenceRequest",
    "CentrifugoPresenceResponse",
    "CentrifugoPresenceResult",
    "CentrifugoClientInfo",
    # Presence Stats API
    "CentrifugoPresenceStatsRequest",
    "CentrifugoPresenceStatsResponse",
    "CentrifugoPresenceStatsResult",
    # History API
    "CentrifugoHistoryRequest",
    "CentrifugoHistoryResponse",
    "CentrifugoHistoryResult",
    "CentrifugoPublication",
    "CentrifugoStreamPosition",
]
