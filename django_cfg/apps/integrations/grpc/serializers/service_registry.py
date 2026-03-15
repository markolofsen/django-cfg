"""
DRF serializers for gRPC Service Registry API.

These serializers define the structure for service registry endpoints
that provide detailed information about registered gRPC services and their methods.
"""

from rest_framework import serializers


class ServiceSummarySerializer(serializers.Serializer):
    """Summary information for a single service."""

    name = serializers.CharField(help_text="Service name (e.g., myapp.UserService)")
    full_name = serializers.CharField(help_text="Full service name with package")
    package = serializers.CharField(help_text="Package name")
    methods_count = serializers.IntegerField(help_text="Number of methods in service")
    total_requests = serializers.IntegerField(
        default=0, help_text="Total requests to this service"
    )
    success_rate = serializers.FloatField(
        default=0.0, help_text="Success rate percentage"
    )
    avg_duration_ms = serializers.FloatField(
        default=0.0, help_text="Average duration in milliseconds"
    )
    last_activity_at = serializers.CharField(
        allow_null=True, required=False, help_text="Last activity timestamp"
    )


class ServiceListSerializer(serializers.Serializer):
    """List of services response."""

    services = ServiceSummarySerializer(
        many=True, default=list, help_text="List of services"
    )
    total_services = serializers.IntegerField(help_text="Total number of services")


class MethodInfoSerializer(serializers.Serializer):
    """Information about a service method."""

    name = serializers.CharField(help_text="Method name")
    full_name = serializers.CharField(help_text="Full method name (/service/method)")
    request_type = serializers.CharField(
        default="", allow_blank=True, help_text="Request message type"
    )
    response_type = serializers.CharField(
        default="", allow_blank=True, help_text="Response message type"
    )
    streaming = serializers.BooleanField(
        default=False, help_text="Whether method uses streaming"
    )
    auth_required = serializers.BooleanField(
        default=False, help_text="Whether authentication is required"
    )


class ServiceStatsSerializer(serializers.Serializer):
    """Service statistics."""

    total_requests = serializers.IntegerField(default=0, help_text="Total requests")
    successful = serializers.IntegerField(default=0, help_text="Successful requests")
    errors = serializers.IntegerField(default=0, help_text="Failed requests")
    success_rate = serializers.FloatField(
        default=0.0, help_text="Success rate percentage"
    )
    avg_duration_ms = serializers.FloatField(
        default=0.0, help_text="Average duration in milliseconds"
    )
    last_24h_requests = serializers.IntegerField(
        default=0, help_text="Requests in last 24 hours"
    )


class RecentErrorSerializer(serializers.Serializer):
    """Recent error information."""

    method = serializers.CharField(help_text="Method name where error occurred")
    error_message = serializers.CharField(help_text="Error message")
    grpc_status_code = serializers.CharField(help_text="gRPC status code")
    occurred_at = serializers.CharField(
        help_text="When error occurred (ISO timestamp)"
    )


class ServiceDetailSerializer(serializers.Serializer):
    """Detailed information about a service."""

    name = serializers.CharField(help_text="Service name")
    full_name = serializers.CharField(help_text="Full service name with package")
    package = serializers.CharField(help_text="Package name")
    description = serializers.CharField(
        default="", allow_blank=True, help_text="Service description from docstring"
    )
    file_path = serializers.CharField(
        default="", allow_blank=True, help_text="Path to service file"
    )
    class_name = serializers.CharField(help_text="Service class name")
    base_class = serializers.CharField(
        default="", allow_blank=True, help_text="Base class name"
    )
    methods = MethodInfoSerializer(many=True, default=list, help_text="Service methods")
    stats = ServiceStatsSerializer(help_text="Service statistics")
    recent_errors = RecentErrorSerializer(
        many=True, default=list, help_text="Recent errors"
    )


class MethodStatsSerializer(serializers.Serializer):
    """Statistics for a single method."""

    class Meta:
        ref_name = 'GRPCServiceRegistryMethodStats'  # Unique name for OpenAPI schema

    total_requests = serializers.IntegerField(default=0, help_text="Total requests")
    successful = serializers.IntegerField(default=0, help_text="Successful requests")
    errors = serializers.IntegerField(default=0, help_text="Failed requests")
    success_rate = serializers.FloatField(
        default=0.0, help_text="Success rate percentage"
    )
    avg_duration_ms = serializers.FloatField(
        default=0.0, help_text="Average duration in milliseconds"
    )
    p50_duration_ms = serializers.FloatField(
        default=0.0, help_text="P50 duration in milliseconds"
    )
    p95_duration_ms = serializers.FloatField(
        default=0.0, help_text="P95 duration in milliseconds"
    )
    p99_duration_ms = serializers.FloatField(
        default=0.0, help_text="P99 duration in milliseconds"
    )


class MethodSummarySerializer(serializers.Serializer):
    """Summary information for a method."""

    name = serializers.CharField(help_text="Method name")
    full_name = serializers.CharField(help_text="Full method path")
    service_name = serializers.CharField(help_text="Service name")
    request_type = serializers.CharField(
        default="", allow_blank=True, help_text="Request message type"
    )
    response_type = serializers.CharField(
        default="", allow_blank=True, help_text="Response message type"
    )
    stats = MethodStatsSerializer(help_text="Method statistics")


class ServiceMethodsSerializer(serializers.Serializer):
    """List of methods for a service."""

    service_name = serializers.CharField(help_text="Service name")
    methods = MethodSummarySerializer(many=True, default=list, help_text="List of methods")
    total_methods = serializers.IntegerField(help_text="Total number of methods")


class MethodListSerializer(serializers.Serializer):
    """List of methods response (for monitoring endpoint)."""

    methods = MethodSummarySerializer(many=True, default=list, help_text="List of methods")
    total_methods = serializers.IntegerField(help_text="Total number of methods")


class RequestSchemaField(serializers.Serializer):
    """Schema field information."""

    name = serializers.CharField(help_text="Field name")
    type = serializers.CharField(help_text="Field type")
    required = serializers.BooleanField(
        default=False, help_text="Whether field is required"
    )
    description = serializers.CharField(
        default="", allow_blank=True, help_text="Field description"
    )


class RequestSchemaSerializer(serializers.Serializer):
    """Request message schema."""

    fields = RequestSchemaField(many=True, default=list, help_text="Schema fields")


class RecentRequestSerializer(serializers.Serializer):
    """Recent request information."""

    id = serializers.IntegerField(help_text="Database ID")
    request_id = serializers.CharField(help_text="Request ID")
    service_name = serializers.CharField(help_text="Service name")
    method_name = serializers.CharField(help_text="Method name")
    status = serializers.CharField(help_text="Request status")
    duration_ms = serializers.IntegerField(default=0, help_text="Duration in milliseconds")
    grpc_status_code = serializers.CharField(
        default="", allow_blank=True, help_text="gRPC status code"
    )
    error_message = serializers.CharField(
        default="", allow_blank=True, help_text="Error message if failed"
    )
    created_at = serializers.CharField(help_text="Request timestamp")
    client_ip = serializers.CharField(
        default="", allow_blank=True, help_text="Client IP address"
    )
    # User information
    user_id = serializers.IntegerField(
        allow_null=True, required=False, help_text="User ID (if authenticated)"
    )
    username = serializers.CharField(
        default="", allow_blank=True, allow_null=True, help_text="Username (if authenticated)"
    )
    is_authenticated = serializers.BooleanField(
        default=False, help_text="Whether request was authenticated"
    )
    # API Key information
    api_key_id = serializers.IntegerField(
        allow_null=True, required=False, help_text="API Key ID (if used)"
    )
    api_key_name = serializers.CharField(
        default="", allow_blank=True, allow_null=True, help_text="API Key name (if used)"
    )


class MethodDetailSerializer(serializers.Serializer):
    """Detailed information about a method."""

    name = serializers.CharField(help_text="Method name")
    full_name = serializers.CharField(help_text="Full method path")
    service_name = serializers.CharField(help_text="Service name")
    request_type = serializers.CharField(
        default="", allow_blank=True, help_text="Request message type"
    )
    response_type = serializers.CharField(
        default="", allow_blank=True, help_text="Response message type"
    )
    streaming = serializers.BooleanField(
        default=False, help_text="Whether method uses streaming"
    )
    auth_required = serializers.BooleanField(
        default=False, help_text="Whether authentication is required"
    )
    description = serializers.CharField(
        default="", allow_blank=True, help_text="Method description"
    )
    request_schema = RequestSchemaSerializer(help_text="Request message schema")
    response_schema = RequestSchemaSerializer(help_text="Response message schema")
    stats = MethodStatsSerializer(help_text="Method statistics")
    recent_requests = RecentRequestSerializer(
        many=True, default=list, help_text="Recent requests"
    )
    error_distribution = serializers.DictField(
        default=dict, help_text="Error distribution by status code"
    )


__all__ = [
    "ServiceSummarySerializer",
    "ServiceListSerializer",
    "ServiceDetailSerializer",
    "ServiceStatsSerializer",
    "MethodInfoSerializer",
    "MethodSummarySerializer",
    "ServiceMethodsSerializer",
    "MethodListSerializer",
    "MethodStatsSerializer",
    "MethodDetailSerializer",
    "RecentErrorSerializer",
    "RecentRequestSerializer",
    "RequestSchemaSerializer",
    "RequestSchemaField",
]
