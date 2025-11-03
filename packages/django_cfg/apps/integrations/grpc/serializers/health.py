"""
Health check serializer for gRPC monitoring API.
"""

from pydantic import BaseModel, Field


class GRPCHealthCheckSerializer(BaseModel):
    """gRPC health check response."""

    status: str = Field(description="Health status: healthy or unhealthy")
    server_host: str = Field(description="Configured gRPC server host")
    server_port: int = Field(description="Configured gRPC server port")
    enabled: bool = Field(description="Whether gRPC is enabled")
    timestamp: str = Field(description="Current timestamp")


__all__ = ["GRPCHealthCheckSerializer"]
