"""django_grpc.config.metrics — In-memory metrics configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MetricsConfig(BaseModel):
    """In-memory gRPC metrics collector configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True, description="Enable in-memory metrics collection")
    response_time_ttl: float = Field(
        default=3600.0,
        ge=60.0,
        le=86400.0,
        description="TTL in seconds for in-memory response time history (prevents unbounded growth)",
    )
    # H-5: optional Prometheus export. Requires `prometheus_client` package.
    # When True and prometheus_client is installed, MetricsCollector uses
    # Counter/Histogram objects with standard gRPC Prometheus label names:
    #   grpc_server_started_total{grpc_service, grpc_method, grpc_type}
    #   grpc_server_handled_total{grpc_service, grpc_method, grpc_type, grpc_code}
    #   grpc_server_handling_seconds{grpc_service, grpc_method, grpc_type}
    #   grpc_server_msg_received_total{grpc_service, grpc_method, grpc_type}
    #   grpc_server_msg_sent_total{grpc_service, grpc_method, grpc_type}
    prometheus_enabled: bool = Field(
        default=False,
        description="Export metrics using prometheus_client (requires prometheus_client package)",
    )


__all__ = ["MetricsConfig"]
