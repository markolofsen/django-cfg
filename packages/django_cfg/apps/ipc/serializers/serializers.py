"""
Serializers for RPC Dashboard API.

DRF serializers for consistent API responses with type hints.
"""


from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response."""

    redis_connected = serializers.BooleanField(
        help_text="Whether Redis is connected"
    )
    stream_exists = serializers.BooleanField(
        help_text="Whether the request stream exists"
    )
    stream_length = serializers.IntegerField(
        help_text="Number of entries in the stream"
    )
    consumer_group_exists = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether the consumer group exists"
    )
    recent_activity = serializers.BooleanField(
        help_text="Whether there was recent activity (last 5 min)"
    )
    last_request_time = serializers.CharField(
        required=False,
        allow_null=True,
        default=None,
        help_text="ISO timestamp of last request"
    )
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Error message if any"
    )


class OverviewStatsSerializer(serializers.Serializer):
    """Serializer for overview statistics."""

    redis_connected = serializers.BooleanField(
        required=False,
        help_text="Whether Redis is connected"
    )
    total_requests_today = serializers.IntegerField(
        help_text="Total requests processed today"
    )
    total_requests_hour = serializers.IntegerField(
        required=False,
        default=0,
        help_text="Total requests in the last hour"
    )
    active_methods = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of active RPC methods"
    )
    top_method = serializers.CharField(
        allow_null=True,
        help_text="Most frequently called method"
    )
    method_counts = serializers.DictField(
        required=False,
        help_text="Count of requests per method"
    )
    avg_response_time_ms = serializers.FloatField(
        help_text="Average response time in milliseconds"
    )
    success_rate = serializers.FloatField(
        help_text="Success rate percentage"
    )
    error_rate = serializers.FloatField(
        required=False,
        default=0.0,
        help_text="Error rate percentage"
    )
    timestamp = serializers.CharField(
        required=False,
        help_text="ISO timestamp of the stats"
    )
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Error message if any"
    )


class RPCRequestSerializer(serializers.Serializer):
    """Serializer for individual RPC request."""

    id = serializers.CharField(
        required=False,
        help_text="Stream entry ID"
    )
    request_id = serializers.CharField(
        required=False,
        help_text="Unique request ID"
    )
    timestamp = serializers.CharField(
        help_text="ISO timestamp of the request"
    )
    method = serializers.CharField(
        allow_null=True,
        help_text="RPC method name"
    )
    params = serializers.DictField(
        allow_null=True,
        required=False,
        help_text="Request parameters"
    )
    correlation_id = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Correlation ID for tracking"
    )
    source = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Source of the request"
    )


class RecentRequestsSerializer(serializers.Serializer):
    """Serializer for recent requests response."""

    requests = serializers.ListField(
        child=RPCRequestSerializer(),
        help_text="List of recent RPC requests"
    )
    count = serializers.IntegerField(
        help_text="Number of requests returned"
    )
    total_available = serializers.IntegerField(
        help_text="Total number of requests available"
    )


class NotificationTypeStatsSerializer(serializers.Serializer):
    """Serializer for notification type statistics."""

    user_activity = serializers.IntegerField(default=0)
    system_alert = serializers.IntegerField(default=0)
    error_notification = serializers.IntegerField(default=0)
    info_message = serializers.IntegerField(default=0)


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""

    total_sent = serializers.IntegerField(
        help_text="Total notifications sent"
    )
    delivery_rate = serializers.FloatField(
        help_text="Delivery success rate percentage"
    )
    by_type = serializers.DictField(
        required=False,
        help_text="Breakdown by notification type"
    )
    recent = serializers.ListField(
        required=False,
        help_text="Recent notifications"
    )
    last_sent = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="ISO timestamp of last notification"
    )
    timestamp = serializers.CharField(
        required=False,
        help_text="ISO timestamp of the stats"
    )
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Error message if any"
    )


class MethodStatSerializer(serializers.Serializer):
    """Serializer for individual method statistics."""

    method = serializers.CharField(
        help_text="RPC method name"
    )
    count = serializers.IntegerField(
        help_text="Number of calls"
    )
    percentage = serializers.FloatField(
        help_text="Percentage of total calls"
    )
    avg_time_ms = serializers.FloatField(
        required=False,
        help_text="Average execution time in milliseconds"
    )
    avg_time = serializers.FloatField(
        required=False,
        help_text="Average execution time (alternative field)"
    )
    success_rate = serializers.FloatField(
        required=False,
        default=100.0,
        help_text="Success rate percentage"
    )
    last_called = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="ISO timestamp of last call"
    )


class MethodStatsSerializer(serializers.Serializer):
    """Serializer for method statistics response."""

    methods = serializers.ListField(
        child=MethodStatSerializer(),
        help_text="List of method statistics"
    )
    count = serializers.IntegerField(
        help_text="Total number of methods"
    )
    total_calls = serializers.IntegerField(
        help_text="Total calls across all methods"
    )
