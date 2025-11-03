"""
Pydantic serializers for gRPC Testing API.

These serializers define the structure for testing endpoints
that provide example payloads and test logs.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GRPCExampleSerializer(BaseModel):
    """Example payload for a gRPC method."""

    service: str = Field(..., description="Service name")
    method: str = Field(..., description="Method name")
    description: str = Field(..., description="Method description")
    payload_example: Dict[str, Any] = Field(
        ..., description="Example request payload"
    )
    expected_response: Dict[str, Any] = Field(
        ..., description="Example expected response"
    )
    metadata_example: Dict[str, str] = Field(
        default_factory=dict, description="Example metadata (headers)"
    )


class GRPCExamplesListSerializer(BaseModel):
    """List of examples response."""

    examples: List[GRPCExampleSerializer] = Field(
        default_factory=list, description="List of examples"
    )
    total_examples: int = Field(..., description="Total number of examples")


class GRPCTestLogSerializer(BaseModel):
    """Single test log entry."""

    request_id: str = Field(..., description="Request ID")
    service: str = Field(..., description="Service name")
    method: str = Field(..., description="Method name")
    status: str = Field(..., description="Request status (success, error, etc.)")
    grpc_status_code: Optional[str] = Field(
        None, description="gRPC status code if available"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    created_at: str = Field(..., description="Request timestamp (ISO format)")
    user: Optional[str] = Field(None, description="User who made the request")


class GRPCTestLogsSerializer(BaseModel):
    """List of test logs response."""

    logs: List[GRPCTestLogSerializer] = Field(
        default_factory=list, description="List of test logs"
    )
    count: int = Field(..., description="Number of logs returned")
    total_available: int = Field(..., description="Total logs available")
    has_more: bool = Field(False, description="Whether more logs are available")


class GRPCCallRequestSerializer(BaseModel):
    """Request to call a gRPC method (for future implementation)."""

    service: str = Field(..., description="Service name to call")
    method: str = Field(..., description="Method name to call")
    payload: Dict[str, Any] = Field(..., description="Request payload")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Request metadata (headers)"
    )
    timeout_ms: int = Field(5000, description="Request timeout in milliseconds")


class GRPCCallResponseSerializer(BaseModel):
    """Response from calling a gRPC method."""

    success: bool = Field(..., description="Whether call was successful")
    request_id: str = Field(..., description="Request ID for tracking")
    service: str = Field(..., description="Service name")
    method: str = Field(..., description="Method name")
    status: str = Field(..., description="Request status")
    grpc_status_code: str = Field(..., description="gRPC status code")
    duration_ms: int = Field(..., description="Call duration in milliseconds")
    response: Optional[str] = Field(
        None, description="Response data if successful (JSON string)"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Response metadata"
    )
    timestamp: str = Field(..., description="Response timestamp (ISO format)")


__all__ = [
    "GRPCExampleSerializer",
    "GRPCExamplesListSerializer",
    "GRPCTestLogSerializer",
    "GRPCTestLogsSerializer",
    "GRPCCallRequestSerializer",
    "GRPCCallResponseSerializer",
]
