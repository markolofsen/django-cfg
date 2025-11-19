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
    relative_schema_url = serializers.CharField()
    api_url = serializers.CharField()
    relative_api_url = serializers.CharField()
    apps = serializers.ListField(child=serializers.CharField())


class ZonesSummaryStatsSerializer(serializers.Serializer):
    """Summary statistics for API zones."""
    total_apps = serializers.IntegerField()
    total_endpoints = serializers.IntegerField()
    total_zones = serializers.IntegerField()


class APIZonesSummarySerializer(serializers.Serializer):
    """API zones summary serializer."""
    zones = APIZoneSerializer(many=True)
    summary = ZonesSummaryStatsSerializer()
