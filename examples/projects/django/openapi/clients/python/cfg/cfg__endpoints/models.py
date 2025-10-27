from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EndpointsStatus(BaseModel):
    """
    Serializer for overall endpoints status response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    status: str = Field(description='Overall status: healthy, degraded, or unhealthy')
    timestamp: str = Field(description='Timestamp of the check')
    total_endpoints: int = Field(description='Total number of endpoints checked')
    healthy: int = Field(description='Number of healthy endpoints')
    unhealthy: int = Field(description='Number of unhealthy endpoints')
    warnings: int = Field(description='Number of endpoints with warnings')
    errors: int = Field(description='Number of endpoints with errors')
    skipped: int = Field(description='Number of skipped endpoints')
    endpoints: list[Any] = Field(description='List of all endpoints with their status')



class URLsList(BaseModel):
    """
    Serializer for URLs list response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    status: str = Field(description='Status: success or error')
    service: str = Field(description='Service name')
    version: str = Field(description='Django-CFG version')
    base_url: str = Field(description='Base URL of the service')
    total_urls: int = Field(description='Total number of registered URLs')
    urls: list[Any] = Field(description='List of all registered URL patterns')



