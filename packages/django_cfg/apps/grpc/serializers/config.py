"""
Pydantic serializers for gRPC configuration and server info.

These serializers define the structure for configuration and server
information endpoints.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class GRPCServerConfigSerializer(BaseModel):
    """gRPC server configuration details."""

    host: str = Field(..., description="Server host address")
    port: int = Field(..., description="Server port")
    enabled: bool = Field(..., description="Whether gRPC server is enabled")
    max_workers: int = Field(..., description="Maximum worker threads")
    max_concurrent_rpcs: Optional[int] = Field(
        None, description="Maximum concurrent RPCs"
    )


class GRPCFrameworkConfigSerializer(BaseModel):
    """gRPC framework configuration details."""

    enabled: bool = Field(..., description="Whether framework is enabled")
    auto_discover: bool = Field(..., description="Auto-discover services")
    services_path: str = Field(..., description="Services discovery path pattern")
    interceptors: List[str] = Field(
        default_factory=list, description="Registered interceptors"
    )


class GRPCFeaturesSerializer(BaseModel):
    """gRPC features configuration."""

    jwt_auth: bool = Field(..., description="JWT authentication enabled")
    request_logging: bool = Field(..., description="Request logging enabled")
    metrics: bool = Field(..., description="Metrics collection enabled")
    reflection: bool = Field(..., description="gRPC reflection enabled")


class GRPCConfigSerializer(BaseModel):
    """Complete gRPC configuration response."""

    server: GRPCServerConfigSerializer = Field(..., description="Server configuration")
    framework: GRPCFrameworkConfigSerializer = Field(
        ..., description="Framework configuration"
    )
    features: GRPCFeaturesSerializer = Field(..., description="Feature flags")
    registered_services: int = Field(..., description="Number of registered services")
    total_methods: int = Field(..., description="Total number of methods")


class GRPCServiceInfoSerializer(BaseModel):
    """Information about a single gRPC service."""

    name: str = Field(..., description="Service name")
    methods: List[str] = Field(default_factory=list, description="Service methods")
    full_name: str = Field(..., description="Full service name with package")
    description: str = Field("", description="Service description")


class GRPCInterceptorInfoSerializer(BaseModel):
    """Information about an interceptor."""

    name: str = Field(..., description="Interceptor name")
    enabled: bool = Field(..., description="Whether interceptor is enabled")


class GRPCStatsSerializer(BaseModel):
    """Runtime statistics summary."""

    total_requests: int = Field(..., description="Total number of requests")
    success_rate: float = Field(..., description="Success rate percentage")
    avg_duration_ms: float = Field(..., description="Average duration in milliseconds")


class GRPCServerInfoSerializer(BaseModel):
    """Complete gRPC server information response."""

    server_status: str = Field(..., description="Server status (running, stopped)")
    address: str = Field(..., description="Server address (host:port)")
    started_at: Optional[str] = Field(None, description="Server start timestamp")
    uptime_seconds: Optional[int] = Field(None, description="Server uptime in seconds")
    services: List[GRPCServiceInfoSerializer] = Field(
        default_factory=list, description="Registered services"
    )
    interceptors: List[GRPCInterceptorInfoSerializer] = Field(
        default_factory=list, description="Active interceptors"
    )
    stats: GRPCStatsSerializer = Field(..., description="Runtime statistics")


__all__ = [
    "GRPCConfigSerializer",
    "GRPCServerInfoSerializer",
    "GRPCServerConfigSerializer",
    "GRPCFrameworkConfigSerializer",
    "GRPCFeaturesSerializer",
    "GRPCServiceInfoSerializer",
    "GRPCInterceptorInfoSerializer",
    "GRPCStatsSerializer",
]
