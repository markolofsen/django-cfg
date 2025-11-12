"""
Channel statistics serializers for Centrifugo monitoring API.
"""

from rest_framework import serializers


class ChannelStatsSerializer(serializers.Serializer):
    """Statistics per channel."""

    channel = serializers.CharField(help_text="Channel name")
    total = serializers.IntegerField(help_text="Total publishes to this channel")
    successful = serializers.IntegerField(help_text="Successful publishes")
    failed = serializers.IntegerField(help_text="Failed publishes")
    avg_duration_ms = serializers.FloatField(help_text="Average duration")
    avg_acks = serializers.FloatField(help_text="Average ACKs received")
    last_activity_at = serializers.CharField(allow_null=True, help_text="Last activity timestamp (ISO format)")


class ChannelListSerializer(serializers.Serializer):
    """List of channel statistics."""

    channels = ChannelStatsSerializer(many=True, help_text="Channel statistics")
    total_channels = serializers.IntegerField(help_text="Total number of channels")


__all__ = ["ChannelStatsSerializer", "ChannelListSerializer"]
