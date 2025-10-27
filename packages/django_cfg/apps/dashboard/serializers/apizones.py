"""
API Zones Serializers

Serializers for OpenAPI zones/groups endpoints.
"""

from rest_framework import serializers


class APIZoneSerializer(serializers.Serializer):
    """OpenAPI zone/group serializer."""
    name = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    app_count = serializers.IntegerField()
    endpoint_count = serializers.IntegerField()
    status = serializers.CharField()
    schema_url = serializers.CharField()
    api_url = serializers.CharField()
    apps = serializers.ListField(child=serializers.CharField())


class APIZonesSummarySerializer(serializers.Serializer):
    """API zones summary serializer."""
    zones = APIZoneSerializer(many=True)
    summary = serializers.DictField()
