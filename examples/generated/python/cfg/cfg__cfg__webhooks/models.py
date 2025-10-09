from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WebhookResponse(BaseModel):
    """
    Serializer for webhook processing response. Standard response format for all
    webhook endpoints.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = Field(description='Whether webhook was processed successfully')
    message: str = Field(description='Processing result message', max_length=500)
    payment_id: str = Field(None, description='Internal payment ID', max_length=256)
    provider_payment_id: str = Field(None, description='Provider payment ID', max_length=256)
    processed_at: str = Field(None, description='Processing timestamp')



class WebhookHealth(BaseModel):
    """
    Serializer for webhook health check response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    status: str = Field(description='Health status', max_length=20)
    timestamp: str = Field(description='Check timestamp')
    providers: str = Field(description='Provider health status')



class SupportedProviders(BaseModel):
    """
    Serializer for supported providers response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = Field(description='Request success status')
    providers: str = Field(description='List of supported providers')
    total_count: int = Field(description='Total number of providers')
    timestamp: str = Field(description='Response timestamp')



class WebhookStats(BaseModel):
    """
    Serializer for comprehensive webhook statistics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total: int = ...
    successful: int = ...
    failed: int = ...
    pending: int = ...
    success_rate: float = ...
    providers: dict[str, Any] = Field(description='Statistics by provider')
    last_24h: dict[str, Any] = Field(description='Events in last 24 hours')
    avg_response_time: float = ...
    max_response_time: int = ...



class WebhookResponseRequest(BaseModel):
    """
    Serializer for webhook processing response. Standard response format for all
    webhook endpoints.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = Field(description='Whether webhook was processed successfully')
    message: str = Field(description='Processing result message', min_length=1, max_length=500)
    payment_id: str = Field(None, description='Internal payment ID', min_length=1, max_length=256)
    provider_payment_id: str = Field(None, description='Provider payment ID', min_length=1, max_length=256)
    processed_at: str = Field(None, description='Processing timestamp')



