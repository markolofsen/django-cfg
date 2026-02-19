"""Centrifugo UI models for Streamlit admin.

WebSocket channel and publish presentation models.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChannelInfo(BaseModel):
    """Channel information for display."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    subscribers: int = Field(ge=0, default=0)
    presence: bool = False
    history: bool = False
    last_activity: str | None = None  # ISO timestamp string from API


class CentrifugoHealth(BaseModel):
    """Centrifugo health status for display."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    status: str = "unknown"  # healthy, unhealthy, error
    nodes: int = Field(ge=0, default=0)
    clients: int = Field(ge=0, default=0)
    channels: int = Field(ge=0, default=0)
    uptime: int | None = None  # seconds


class PublishRecord(BaseModel):
    """Publish record for display."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: str
    channel: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime | None = None
