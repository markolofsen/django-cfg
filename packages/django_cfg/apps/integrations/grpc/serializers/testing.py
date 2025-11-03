"""
DRF serializers for gRPC Testing API.

These serializers define the structure for testing endpoints
that provide example payloads and test logs.
"""

from rest_framework import serializers


class GRPCExampleSerializer(serializers.Serializer):
    """Example payload for a gRPC method."""

    service = serializers.CharField(help_text="Service name")
    method = serializers.CharField(help_text="Method name")
    description = serializers.CharField(help_text="Method description")
    payload_example = serializers.DictField(help_text="Example request payload")
    expected_response = serializers.DictField(help_text="Example expected response")
    metadata_example = serializers.DictField(
        default=dict, help_text="Example metadata (headers)"
    )


class GRPCExamplesListSerializer(serializers.Serializer):
    """List of examples response."""

    examples = GRPCExampleSerializer(
        many=True, default=list, help_text="List of examples"
    )
    total_examples = serializers.IntegerField(help_text="Total number of examples")


class GRPCTestLogSerializer(serializers.Serializer):
    """Single test log entry."""

    request_id = serializers.CharField(help_text="Request ID")
    service = serializers.CharField(help_text="Service name")
    method = serializers.CharField(help_text="Method name")
    status = serializers.CharField(
        help_text="Request status (success, error, etc.)"
    )
    grpc_status_code = serializers.CharField(
        required=False, allow_null=True, help_text="gRPC status code if available"
    )
    error_message = serializers.CharField(
        required=False, allow_null=True, help_text="Error message if failed"
    )
    duration_ms = serializers.IntegerField(
        required=False, allow_null=True, help_text="Duration in milliseconds"
    )
    created_at = serializers.CharField(
        help_text="Request timestamp (ISO format)"
    )
    user = serializers.CharField(
        required=False, allow_null=True, help_text="User who made the request"
    )


class GRPCTestLogsSerializer(serializers.Serializer):
    """List of test logs response."""

    logs = GRPCTestLogSerializer(many=True, default=list, help_text="List of test logs")
    count = serializers.IntegerField(help_text="Number of logs returned")
    total_available = serializers.IntegerField(help_text="Total logs available")
    has_more = serializers.BooleanField(
        default=False, help_text="Whether more logs are available"
    )


class GRPCCallRequestSerializer(serializers.Serializer):
    """Request to call a gRPC method (for future implementation)."""

    service = serializers.CharField(help_text="Service name to call")
    method = serializers.CharField(help_text="Method name to call")
    payload = serializers.DictField(help_text="Request payload")
    metadata = serializers.DictField(
        default=dict, help_text="Request metadata (headers)"
    )
    timeout_ms = serializers.IntegerField(
        default=5000, help_text="Request timeout in milliseconds"
    )


class GRPCCallResponseSerializer(serializers.Serializer):
    """Response from calling a gRPC method."""

    success = serializers.BooleanField(help_text="Whether call was successful")
    request_id = serializers.CharField(help_text="Request ID for tracking")
    service = serializers.CharField(help_text="Service name")
    method = serializers.CharField(help_text="Method name")
    status = serializers.CharField(help_text="Request status")
    grpc_status_code = serializers.CharField(help_text="gRPC status code")
    duration_ms = serializers.IntegerField(help_text="Call duration in milliseconds")
    response = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Response data if successful (JSON string)",
    )
    error = serializers.CharField(
        required=False, allow_null=True, help_text="Error message if failed"
    )
    metadata = serializers.DictField(default=dict, help_text="Response metadata")
    timestamp = serializers.CharField(help_text="Response timestamp (ISO format)")


__all__ = [
    "GRPCExampleSerializer",
    "GRPCExamplesListSerializer",
    "GRPCTestLogSerializer",
    "GRPCTestLogsSerializer",
    "GRPCCallRequestSerializer",
    "GRPCCallResponseSerializer",
]
