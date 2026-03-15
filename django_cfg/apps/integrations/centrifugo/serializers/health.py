"""
Health check serializer for Centrifugo monitoring API.
"""

from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Health check response."""

    class Meta:
        ref_name = 'CentrifugoHealthCheck'  # Unique name for OpenAPI schema

    status = serializers.CharField(help_text="Health status: healthy or unhealthy")
    wrapper_url = serializers.CharField(help_text="Configured wrapper URL")
    has_api_key = serializers.BooleanField(help_text="Whether API key is configured")
    timestamp = serializers.CharField(help_text="Current timestamp")


__all__ = ["HealthCheckSerializer"]
