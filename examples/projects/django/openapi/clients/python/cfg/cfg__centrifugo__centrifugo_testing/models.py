from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConnectionTokenResponse(BaseModel):
    """
    Response model for connection token.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    token: str = Field(description='JWT token for WebSocket connection')
    centrifugo_url: str = Field(description='Centrifugo WebSocket URL')
    expires_at: str = Field(description='Token expiration time (ISO 8601)')



class PublishTestResponse(BaseModel):
    """
    Response model for test message publishing.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    success: bool = Field(description='Whether publish succeeded')
    message_id: str = Field(description='Unique message ID')
    channel: str = Field(description='Target channel')
    acks_received: int = Field(None, description='Number of ACKs received')
    delivered: bool = Field(None, description='Whether message was delivered')
    error: str | None = Field(None, description='Error message if failed')



class ManualAckResponse(BaseModel):
    """
    Response model for manual ACK.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    success: bool = Field(description='Whether ACK was sent successfully')
    message_id: str = Field(description='Message ID that was acknowledged')
    error: str | None = Field(None, description='Error message if failed')



class ConnectionTokenRequestRequest(BaseModel):
    """
    Request model for connection token generation.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    user_id: str = Field(description='User ID for the connection')
    channels: list[str] = Field(None, description='List of channels to authorize')



class PublishTestRequestRequest(BaseModel):
    """
    Request model for test message publishing.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    channel: str = Field(description='Target channel name')
    data: Any = Field(description='Message data (any JSON object)')
    wait_for_ack: bool = Field(None, description='Wait for client acknowledgment')
    ack_timeout: int = Field(None, description='ACK timeout in seconds', ge=1, le=60)



class ManualAckRequestRequest(BaseModel):
    """
    Request model for manual ACK sending.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    message_id: str = Field(description='Message ID to acknowledge')
    client_id: str = Field(description='Client ID sending the ACK')



