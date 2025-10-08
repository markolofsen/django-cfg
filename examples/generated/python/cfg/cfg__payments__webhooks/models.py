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
    Serializer for webhook statistics response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_webhooks: int = Field(description='Total webhooks processed')
    successful_webhooks: int = Field(description='Successfully processed webhooks')
    failed_webhooks: int = Field(description='Failed webhook processing attempts')
    success_rate: float = Field(description='Success rate percentage')
    providers: str = Field(description='Per-provider statistics')



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



