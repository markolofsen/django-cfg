"""
Services serializers for gRPC monitoring API.
"""

from rest_framework import serializers


class MethodStatsSerializer(serializers.Serializer):
    """Statistics for a single gRPC method."""

    method_name = serializers.CharField(help_text="Method name")
    service_name = serializers.CharField(help_text="Service name")
    total = serializers.IntegerField(help_text="Total requests")
    successful = serializers.IntegerField(help_text="Successful requests")
    errors = serializers.IntegerField(help_text="Error requests")
    avg_duration_ms = serializers.FloatField(help_text="Average duration")
    last_activity_at = serializers.CharField(
        allow_null=True, help_text="Last activity timestamp"
    )


class MethodListSerializer(serializers.Serializer):
    """List of gRPC methods with statistics."""

    methods = MethodStatsSerializer(many=True, help_text="Method statistics")
    total_methods = serializers.IntegerField(help_text="Total number of methods")


__all__ = [
    "MethodStatsSerializer",
    "MethodListSerializer",
]
