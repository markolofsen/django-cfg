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



class QuickHealth(BaseModel):
    """
    Serializer for quick health check response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    status: str = Field(description='Quick health status: ok or error')
    timestamp: str = Field(description='Timestamp of the health check')
    error: str = Field(None, description='Error message if health check failed')



