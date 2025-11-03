"""
Health check serializer for Centrifugo monitoring API.
"""

from pydantic import BaseModel, Field


class HealthCheckSerializer(BaseModel):
    """Health check response."""

    status: str = Field(description="Health status: healthy or unhealthy")
    wrapper_url: str = Field(description="Configured wrapper URL")
    has_api_key: bool = Field(description="Whether API key is configured")
    timestamp: str = Field(description="Current timestamp")


__all__ = ["HealthCheckSerializer"]
