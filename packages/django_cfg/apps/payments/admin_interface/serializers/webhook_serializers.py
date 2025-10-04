"""
Webhook Serializers for Admin Interface.

DRF serializers for webhook management in admin dashboard.
"""

from rest_framework import serializers
from datetime import datetime
from typing import Dict, Any


class WebhookEventSerializer(serializers.Serializer):
    """
    Serializer for individual webhook event.
    """
    id = serializers.IntegerField(read_only=True)
    provider = serializers.CharField(max_length=50)
    event_type = serializers.CharField(max_length=100)
    status = serializers.ChoiceField(choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('retry', 'Retry'),
    ])
    timestamp = serializers.DateTimeField()
    payload_size = serializers.IntegerField(help_text="Size in bytes")
    response_time = serializers.IntegerField(help_text="Response time in ms")
    retry_count = serializers.IntegerField(default=0)
    error_message = serializers.CharField(max_length=500, required=False, allow_blank=True)
    payload_preview = serializers.CharField(max_length=200, required=False, allow_blank=True)
    response_status_code = serializers.IntegerField(required=False)
    webhook_url = serializers.URLField(required=False)


class WebhookEventListSerializer(serializers.Serializer):
    """
    Serializer for paginated webhook events list.
    """
    events = WebhookEventSerializer(many=True)
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    per_page = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class WebhookProviderStatsSerializer(serializers.Serializer):
    """
    Serializer for provider-specific webhook statistics.
    """
    total = serializers.IntegerField()
    successful = serializers.IntegerField()
    failed = serializers.IntegerField()
    pending = serializers.IntegerField(default=0)
    success_rate = serializers.FloatField()


class WebhookStatsSerializer(serializers.Serializer):
    """
    Serializer for comprehensive webhook statistics.
    """
    total = serializers.IntegerField()
    successful = serializers.IntegerField()
    failed = serializers.IntegerField()
    pending = serializers.IntegerField()
    success_rate = serializers.FloatField()
    
    # Provider breakdown
    providers = serializers.DictField(
        child=WebhookProviderStatsSerializer(),
        help_text="Statistics by provider"
    )
    
    # Time-based stats
    last_24h = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Events in last 24 hours"
    )
    
    # Performance metrics
    avg_response_time = serializers.FloatField()
    max_response_time = serializers.IntegerField()


class WebhookActionSerializer(serializers.Serializer):
    """
    Serializer for webhook actions (retry, clear, etc.).
    """
    action = serializers.ChoiceField(choices=[
        ('retry', 'Retry'),
        ('clear', 'Clear'),
        ('retry_failed', 'Retry Failed'),
    ])
    event_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of event IDs to process"
    )


class WebhookActionResultSerializer(serializers.Serializer):
    """
    Serializer for webhook action results.
    """
    success = serializers.BooleanField()
    message = serializers.CharField(max_length=200)
    event_id = serializers.IntegerField(required=False)
    processed_count = serializers.IntegerField(required=False)
    failed_count = serializers.IntegerField(required=False)
    errors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of error messages if any"
    )
