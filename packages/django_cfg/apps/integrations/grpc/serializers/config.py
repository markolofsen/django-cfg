"""
DRF serializers for gRPC configuration and server info.

These serializers define the structure for configuration and server
information endpoints.
"""

from rest_framework import serializers


class GRPCServerConfigSerializer(serializers.Serializer):
    """gRPC server configuration details."""

    host = serializers.CharField(help_text="Server host address")
    port = serializers.IntegerField(help_text="Server port")
    enabled = serializers.BooleanField(help_text="Whether gRPC server is enabled")
    max_concurrent_streams = serializers.IntegerField(
        allow_null=True, required=False, help_text="Maximum concurrent streams (async server)"
    )
    max_concurrent_rpcs = serializers.IntegerField(
        allow_null=True, required=False, help_text="Maximum concurrent RPCs"
    )


class GRPCFrameworkConfigSerializer(serializers.Serializer):
    """gRPC framework configuration details."""

    enabled = serializers.BooleanField(help_text="Whether framework is enabled")
    auto_discover = serializers.BooleanField(help_text="Auto-discover services")
    services_path = serializers.CharField(help_text="Services discovery path pattern")
    interceptors = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        help_text="Registered interceptors",
    )


class GRPCFeaturesSerializer(serializers.Serializer):
    """gRPC features configuration."""

    api_key_auth = serializers.BooleanField(help_text="API key authentication enabled")
    request_logging = serializers.BooleanField(help_text="Request logging enabled")
    metrics = serializers.BooleanField(help_text="Metrics collection enabled")
    reflection = serializers.BooleanField(help_text="gRPC reflection enabled")


class GRPCConfigSerializer(serializers.Serializer):
    """Complete gRPC configuration response."""

    server = GRPCServerConfigSerializer(help_text="Server configuration")
    framework = GRPCFrameworkConfigSerializer(help_text="Framework configuration")
    features = GRPCFeaturesSerializer(help_text="Feature flags")
    registered_services = serializers.IntegerField(
        help_text="Number of registered services"
    )
    total_methods = serializers.IntegerField(help_text="Total number of methods")


class GRPCServiceInfoSerializer(serializers.Serializer):
    """Information about a single gRPC service."""

    name = serializers.CharField(help_text="Service name")
    methods = serializers.ListField(
        child=serializers.CharField(), default=list, help_text="Service methods"
    )
    full_name = serializers.CharField(help_text="Full service name with package")
    description = serializers.CharField(
        default="", allow_blank=True, help_text="Service description"
    )


class GRPCInterceptorInfoSerializer(serializers.Serializer):
    """Information about an interceptor."""

    name = serializers.CharField(help_text="Interceptor name")
    enabled = serializers.BooleanField(help_text="Whether interceptor is enabled")


class GRPCStatsSerializer(serializers.Serializer):
    """Runtime statistics summary."""

    total_requests = serializers.IntegerField(help_text="Total number of requests")
    success_rate = serializers.FloatField(help_text="Success rate percentage")
    avg_duration_ms = serializers.FloatField(
        help_text="Average duration in milliseconds"
    )


class GRPCServerInfoSerializer(serializers.Serializer):
    """Complete gRPC server information response."""

    server_status = serializers.CharField(
        help_text="Server status (running, stopped)"
    )
    address = serializers.CharField(help_text="Server address (host:port)")
    started_at = serializers.CharField(
        allow_null=True, required=False, help_text="Server start timestamp"
    )
    uptime_seconds = serializers.IntegerField(
        allow_null=True, required=False, help_text="Server uptime in seconds"
    )
    services = GRPCServiceInfoSerializer(
        many=True, default=list, help_text="Registered services"
    )
    interceptors = GRPCInterceptorInfoSerializer(
        many=True, default=list, help_text="Active interceptors"
    )
    stats = GRPCStatsSerializer(help_text="Runtime statistics")


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
