"""
Health check serializer for gRPC monitoring API.
"""

from rest_framework import serializers


class GRPCHealthCheckSerializer(serializers.Serializer):
    """gRPC health check response."""

    status = serializers.CharField(help_text="Health status: healthy or unhealthy")
    server_host = serializers.CharField(help_text="Configured gRPC server host")
    server_port = serializers.IntegerField(help_text="Configured gRPC server port")
    enabled = serializers.BooleanField(help_text="Whether gRPC is enabled")
    timestamp = serializers.CharField(help_text="Current timestamp")


__all__ = ["GRPCHealthCheckSerializer"]
