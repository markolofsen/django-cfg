"""
Publishes serializers for Centrifugo monitoring API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from rest_framework import serializers


class PublishSerializer(serializers.Serializer):
    """Single publish item for DRF pagination."""

    message_id = serializers.CharField()
    channel = serializers.CharField()
    status = serializers.CharField()
    wait_for_ack = serializers.BooleanField()
    acks_received = serializers.IntegerField()
    acks_expected = serializers.IntegerField(allow_null=True)
    duration_ms = serializers.FloatField(allow_null=True)
    created_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)
    error_code = serializers.CharField(allow_null=True)
    error_message = serializers.CharField(allow_null=True)


class RecentPublishesSerializer(BaseModel):
    """Recent publishes list (DEPRECATED - use DRF pagination instead)."""

    publishes: list[dict] = Field(description="List of recent publishes")
    count: int = Field(description="Number of publishes returned")
    total_available: int = Field(description="Total publishes available")
    offset: int = Field(default=0, description="Current offset for pagination")
    has_more: bool = Field(default=False, description="Whether more results are available")


class TimelineItemSerializer(serializers.Serializer):
    """Single timeline data point for DRF."""

    timestamp = serializers.CharField()
    count = serializers.IntegerField()
    successful = serializers.IntegerField()
    failed = serializers.IntegerField()
    timeout = serializers.IntegerField()


class TimelineResponseSerializer(serializers.Serializer):
    """Timeline response with hourly/daily breakdown for DRF."""

    timeline = TimelineItemSerializer(many=True)
    period_hours = serializers.IntegerField()
    interval = serializers.CharField()


__all__ = [
    "PublishSerializer",
    "RecentPublishesSerializer",
    "TimelineItemSerializer",
    "TimelineResponseSerializer",
]
