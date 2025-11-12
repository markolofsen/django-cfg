"""
Statistics serializers for Centrifugo monitoring API.
"""

from rest_framework import serializers


class CentrifugoOverviewStatsSerializer(serializers.Serializer):
    """Overview statistics for Centrifugo publishes."""

    total = serializers.IntegerField(help_text="Total publishes in period")
    successful = serializers.IntegerField(help_text="Successful publishes")
    failed = serializers.IntegerField(help_text="Failed publishes")
    timeout = serializers.IntegerField(help_text="Timeout publishes")
    success_rate = serializers.FloatField(help_text="Success rate percentage")
    avg_duration_ms = serializers.FloatField(help_text="Average duration in milliseconds")
    avg_acks_received = serializers.FloatField(help_text="Average ACKs received")
    period_hours = serializers.IntegerField(help_text="Statistics period in hours")


__all__ = ["CentrifugoOverviewStatsSerializer"]
