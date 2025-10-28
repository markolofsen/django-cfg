from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CentrifugoChannelsResponse(BaseModel):
    """
    List of active channels response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    error: Any = None
    result: Any = None



class CentrifugoHistoryResponse(BaseModel):
    """
    Channel history response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    error: Any = None
    result: Any = None



class CentrifugoInfoResponse(BaseModel):
    """
    Server info response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    error: Any = None
    result: Any = None



class CentrifugoPresenceResponse(BaseModel):
    """
    Channel presence response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    error: Any = None
    result: Any = None



class CentrifugoPresenceStatsResponse(BaseModel):
    """
    Channel presence stats response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    error: Any = None
    result: Any = None



class CentrifugoChannelsRequestRequest(BaseModel):
    """
    Request to list active channels.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    pattern: str | None = Field(None, description="Pattern to filter channels (e.g., 'user:*')")



class CentrifugoHistoryRequestRequest(BaseModel):
    """
    Request to get channel history.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    channel: str = Field(description='Channel name')
    limit: str | None = Field(None, description='Maximum number of messages to return')
    since: Any = None
    reverse: str | None = Field(None, description='Reverse message order (newest first)')



class CentrifugoPresenceRequestRequest(BaseModel):
    """
    Request to get channel presence.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    channel: str = Field(description='Channel name')



class CentrifugoPresenceStatsRequestRequest(BaseModel):
    """
    Request to get channel presence statistics.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    channel: str = Field(description='Channel name')



