"""
Django CFG Health Check Serializers

DRF serializers for health check endpoints with Tailwind browsable API.
"""

from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response."""

    class Meta:
        ref_name = 'DRFHealthCheck'  # Unique name for OpenAPI schema

    status = serializers.CharField(
        help_text="Overall health status: healthy, degraded, or unhealthy"
    )
    timestamp = serializers.DateTimeField(
        help_text="Timestamp of the health check"
    )
    service = serializers.CharField(
        help_text="Service name"
    )
    version = serializers.CharField(
        help_text="Django-CFG version"
    )
    checks = serializers.DictField(
        help_text="Detailed health checks for databases, cache, and system"
    )
    environment = serializers.DictField(
        help_text="Environment information"
    )
    links = serializers.DictField(
        required=False,
        help_text="Useful API endpoint links"
    )


class LiveHealthSerializer(serializers.Serializer):
    """Serializer for dependency-free liveness response."""

    status = serializers.CharField(
        help_text="Liveness status: ok"
    )
    ok = serializers.BooleanField(
        help_text="Whether the process is alive"
    )
    timestamp = serializers.DateTimeField(
        help_text="Timestamp of the health check"
    )
    service = serializers.CharField(
        help_text="Service name"
    )
    version = serializers.CharField(
        help_text="Django-CFG version"
    )
