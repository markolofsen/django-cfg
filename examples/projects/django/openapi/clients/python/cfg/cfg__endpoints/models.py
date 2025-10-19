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
        extra="forbid",
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
    endpoints: list[dict[str, Any]] = Field(description='List of all endpoints with their status')



