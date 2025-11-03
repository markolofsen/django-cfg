"""
Services serializers for gRPC monitoring API.
"""

from pydantic import BaseModel, Field


class MonitoringServiceStatsSerializer(BaseModel):
    """Statistics for a single gRPC service (monitoring endpoint)."""

    service_name: str = Field(description="Service name")
    total: int = Field(description="Total requests")
    successful: int = Field(description="Successful requests")
    errors: int = Field(description="Error requests")
    avg_duration_ms: float = Field(description="Average duration")
    last_activity_at: str | None = Field(description="Last activity timestamp")


class ServiceListSerializer(BaseModel):
    """List of gRPC services with statistics."""

    services: list[MonitoringServiceStatsSerializer] = Field(description="Service statistics")
    total_services: int = Field(description="Total number of services")


class MethodStatsSerializer(BaseModel):
    """Statistics for a single gRPC method."""

    method_name: str = Field(description="Method name")
    service_name: str = Field(description="Service name")
    total: int = Field(description="Total requests")
    successful: int = Field(description="Successful requests")
    errors: int = Field(description="Error requests")
    avg_duration_ms: float = Field(description="Average duration")
    last_activity_at: str | None = Field(description="Last activity timestamp")


class MethodListSerializer(BaseModel):
    """List of gRPC methods with statistics."""

    methods: list[MethodStatsSerializer] = Field(description="Method statistics")
    total_methods: int = Field(description="Total number of methods")


__all__ = [
    "MonitoringServiceStatsSerializer",
    "ServiceListSerializer",
    "MethodStatsSerializer",
    "MethodListSerializer",
]
