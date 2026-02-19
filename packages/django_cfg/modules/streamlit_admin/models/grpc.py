"""gRPC UI models for Streamlit admin.

Service and method presentation models.
"""

from pydantic import BaseModel, ConfigDict, Field


class ServiceInfo(BaseModel):
    """gRPC service information for display."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    package: str = ""
    methods_count: int = Field(ge=0, default=0)
    total_calls: int = Field(ge=0, default=0)
    error_count: int = Field(ge=0, default=0)
    avg_latency_ms: float = Field(ge=0, default=0.0)
    status: str = "unknown"  # active, inactive, error


class MethodStats(BaseModel):
    """gRPC method statistics for display."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    calls: int = Field(ge=0, default=0)
    errors: int = Field(ge=0, default=0)
    avg_latency_ms: float = Field(ge=0, default=0.0)
    p99_latency_ms: float = Field(ge=0, default=0.0)


class GRPCHealth(BaseModel):
    """gRPC system health for display."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    status: str = "unknown"  # healthy, unhealthy, error
    services_count: int = Field(ge=0, default=0)
    methods_count: int = Field(ge=0, default=0)
    total_calls: int = Field(ge=0, default=0)
    error_rate: float = Field(ge=0, le=100, default=0.0)
