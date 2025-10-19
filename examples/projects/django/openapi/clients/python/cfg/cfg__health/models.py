from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthCheck(BaseModel):
    """
    Serializer for health check response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    status: str = Field(description='Overall health status: healthy, degraded, or unhealthy')
    timestamp: str = Field(description='Timestamp of the health check')
    service: str = Field(description='Service name')
    version: str = Field(description='Django-CFG version')
    checks: dict[str, Any] = Field(description='Detailed health checks for databases, cache, and system')
    environment: dict[str, Any] = Field(description='Environment information')



class QuickHealth(BaseModel):
    """
    Serializer for quick health check response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    status: str = Field(description='Quick health status: ok or error')
    timestamp: str = Field(description='Timestamp of the health check')
    error: str = Field(None, description='Error message if health check failed')



