"""
Health check and configuration serializers for Django-RQ.
"""

from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """
    Health check response serializer.

    Provides overall RQ cluster health status.
    """

    class Meta:
        ref_name = 'RQHealthCheck'  # Unique name for OpenAPI schema

    status = serializers.CharField(help_text="Health status (healthy/degraded/unhealthy)")
    worker_count = serializers.IntegerField(help_text="Total number of active workers")
    queue_count = serializers.IntegerField(help_text="Number of configured queues")
    total_jobs = serializers.IntegerField(help_text="Total jobs across all queues")
    timestamp = serializers.DateTimeField(help_text="Health check timestamp")
    enabled = serializers.BooleanField(help_text="RQ enabled status")
    redis_connected = serializers.BooleanField(help_text="Redis connection status")
    wrapper_url = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Wrapper URL (optional)"
    )
    has_api_key = serializers.BooleanField(
        required=False,
        default=False,
        help_text="API key configured status"
    )


class ScheduleInfoSerializer(serializers.Serializer):
    """Schedule information in config response."""
    func = serializers.CharField()
    queue = serializers.CharField()
    cron = serializers.CharField(allow_null=True, required=False)
    interval = serializers.IntegerField(allow_null=True, required=False)
    scheduled_time = serializers.DateTimeField(allow_null=True, required=False)
    description = serializers.CharField(allow_null=True, required=False)
    timeout = serializers.IntegerField(allow_null=True, required=False)
    result_ttl = serializers.IntegerField(allow_null=True, required=False)
    repeat = serializers.IntegerField(allow_null=True, required=False)


class RQConfigSerializer(serializers.Serializer):
    """
    RQ configuration serializer.

    Returns current RQ configuration from django-cfg.
    """

    enabled = serializers.BooleanField(help_text="RQ enabled status")
    queues = serializers.JSONField(help_text="Configured queues")
    async_mode = serializers.BooleanField(
        default=True, help_text="Async mode enabled"
    )
    show_admin_link = serializers.BooleanField(
        default=True, help_text="Show admin link"
    )
    prometheus_enabled = serializers.BooleanField(
        default=True, help_text="Prometheus metrics enabled"
    )
    api_token_configured = serializers.BooleanField(
        default=False, help_text="API token is configured"
    )
    schedules = serializers.ListField(
        child=ScheduleInfoSerializer(),
        required=False,
        default=list,
        help_text="Scheduled tasks from django-cfg config"
    )
