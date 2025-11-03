"""
Pydantic serializers for gRPC Service Registry API.

These serializers define the structure for service registry endpoints
that provide detailed information about registered gRPC services and their methods.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ServiceSummarySerializer(BaseModel):
    """Summary information for a single service."""

    name: str = Field(..., description="Service name (e.g., myapp.UserService)")
    full_name: str = Field(..., description="Full service name with package")
    package: str = Field(..., description="Package name")
    methods_count: int = Field(..., description="Number of methods in service")
    total_requests: int = Field(0, description="Total requests to this service")
    success_rate: float = Field(0.0, description="Success rate percentage")
    avg_duration_ms: float = Field(0.0, description="Average duration in milliseconds")
    last_activity_at: Optional[str] = Field(None, description="Last activity timestamp")


class ServiceListSerializer(BaseModel):
    """List of services response."""

    services: List[ServiceSummarySerializer] = Field(
        default_factory=list, description="List of services"
    )
    total_services: int = Field(..., description="Total number of services")


class MethodInfoSerializer(BaseModel):
    """Information about a service method."""

    name: str = Field(..., description="Method name")
    full_name: str = Field(..., description="Full method name (/service/method)")
    request_type: str = Field("", description="Request message type")
    response_type: str = Field("", description="Response message type")
    streaming: bool = Field(False, description="Whether method uses streaming")
    auth_required: bool = Field(False, description="Whether authentication is required")


class ServiceStatsSerializer(BaseModel):
    """Service statistics."""

    total_requests: int = Field(0, description="Total requests")
    successful: int = Field(0, description="Successful requests")
    errors: int = Field(0, description="Failed requests")
    success_rate: float = Field(0.0, description="Success rate percentage")
    avg_duration_ms: float = Field(0.0, description="Average duration in milliseconds")
    last_24h_requests: int = Field(0, description="Requests in last 24 hours")


class RecentErrorSerializer(BaseModel):
    """Recent error information."""

    method: str = Field(..., description="Method name where error occurred")
    error_message: str = Field(..., description="Error message")
    grpc_status_code: str = Field(..., description="gRPC status code")
    occurred_at: str = Field(..., description="When error occurred (ISO timestamp)")


class ServiceDetailSerializer(BaseModel):
    """Detailed information about a service."""

    name: str = Field(..., description="Service name")
    full_name: str = Field(..., description="Full service name with package")
    package: str = Field(..., description="Package name")
    description: str = Field("", description="Service description from docstring")
    file_path: str = Field("", description="Path to service file")
    class_name: str = Field(..., description="Service class name")
    base_class: str = Field("", description="Base class name")
    methods: List[MethodInfoSerializer] = Field(
        default_factory=list, description="Service methods"
    )
    stats: ServiceStatsSerializer = Field(..., description="Service statistics")
    recent_errors: List[RecentErrorSerializer] = Field(
        default_factory=list, description="Recent errors"
    )


class MethodStatsSerializer(BaseModel):
    """Statistics for a single method."""

    total_requests: int = Field(0, description="Total requests")
    successful: int = Field(0, description="Successful requests")
    errors: int = Field(0, description="Failed requests")
    success_rate: float = Field(0.0, description="Success rate percentage")
    avg_duration_ms: float = Field(0.0, description="Average duration in milliseconds")
    p50_duration_ms: float = Field(0.0, description="P50 duration in milliseconds")
    p95_duration_ms: float = Field(0.0, description="P95 duration in milliseconds")
    p99_duration_ms: float = Field(0.0, description="P99 duration in milliseconds")


class MethodSummarySerializer(BaseModel):
    """Summary information for a method."""

    name: str = Field(..., description="Method name")
    full_name: str = Field(..., description="Full method path")
    service_name: str = Field(..., description="Service name")
    request_type: str = Field("", description="Request message type")
    response_type: str = Field("", description="Response message type")
    stats: MethodStatsSerializer = Field(..., description="Method statistics")


class ServiceMethodsSerializer(BaseModel):
    """List of methods for a service."""

    service_name: str = Field(..., description="Service name")
    methods: List[MethodSummarySerializer] = Field(
        default_factory=list, description="List of methods"
    )
    total_methods: int = Field(..., description="Total number of methods")


class RequestSchemaField(BaseModel):
    """Schema field information."""

    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type")
    required: bool = Field(False, description="Whether field is required")
    description: str = Field("", description="Field description")


class RequestSchemaSerializer(BaseModel):
    """Request message schema."""

    fields: List[RequestSchemaField] = Field(
        default_factory=list, description="Schema fields"
    )


class RecentRequestSerializer(BaseModel):
    """Recent request information."""

    id: int = Field(..., description="Database ID")
    request_id: str = Field(..., description="Request ID")
    service_name: str = Field(..., description="Service name")
    method_name: str = Field(..., description="Method name")
    status: str = Field(..., description="Request status")
    duration_ms: int = Field(0, description="Duration in milliseconds")
    grpc_status_code: str = Field("", description="gRPC status code")
    error_message: str = Field("", description="Error message if failed")
    created_at: str = Field(..., description="Request timestamp")
    client_ip: str = Field("", description="Client IP address")


class MethodDetailSerializer(BaseModel):
    """Detailed information about a method."""

    name: str = Field(..., description="Method name")
    full_name: str = Field(..., description="Full method path")
    service_name: str = Field(..., description="Service name")
    request_type: str = Field("", description="Request message type")
    response_type: str = Field("", description="Response message type")
    streaming: bool = Field(False, description="Whether method uses streaming")
    auth_required: bool = Field(False, description="Whether authentication is required")
    description: str = Field("", description="Method description")
    request_schema: RequestSchemaSerializer = Field(
        ..., description="Request message schema"
    )
    response_schema: RequestSchemaSerializer = Field(
        ..., description="Response message schema"
    )
    stats: MethodStatsSerializer = Field(..., description="Method statistics")
    recent_requests: List[RecentRequestSerializer] = Field(
        default_factory=list, description="Recent requests"
    )
    error_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Error distribution by status code"
    )


__all__ = [
    "ServiceSummarySerializer",
    "ServiceListSerializer",
    "ServiceDetailSerializer",
    "ServiceStatsSerializer",
    "MethodInfoSerializer",
    "MethodSummarySerializer",
    "ServiceMethodsSerializer",
    "MethodStatsSerializer",
    "MethodDetailSerializer",
    "RecentErrorSerializer",
    "RecentRequestSerializer",
    "RequestSchemaSerializer",
    "RequestSchemaField",
]
