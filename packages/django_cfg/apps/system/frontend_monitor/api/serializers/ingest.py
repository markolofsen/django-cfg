"""
Serializers for the frontend monitor ingest endpoint.
"""

from rest_framework import serializers

from django_cfg.apps.system.frontend_monitor.models.event import FrontendEvent


class FrontendEventIngestSerializer(serializers.Serializer):
    """Validates a single event from the browser."""

    # Required
    event_type = serializers.ChoiceField(choices=FrontendEvent.EventType.choices)
    message = serializers.CharField(max_length=5000)

    # Optional core
    level = serializers.ChoiceField(
        choices=FrontendEvent.Level.choices,
        default=FrontendEvent.Level.INFO,
        required=False,
    )
    stack_trace = serializers.CharField(
        max_length=20000, required=False, allow_blank=True, default=""
    )
    url = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    fingerprint = serializers.CharField(
        max_length=64, required=False, allow_blank=True, default=""
    )

    # Network error context
    http_status = serializers.IntegerField(required=False, allow_null=True, default=None)
    http_method = serializers.CharField(
        max_length=10, required=False, allow_blank=True, default=""
    )
    http_url = serializers.CharField(
        max_length=2000, required=False, allow_blank=True, default=""
    )

    # Client context (UA is extracted server-side too, client can override)
    user_agent = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )

    # Session (assigned by browser)
    session_id = serializers.UUIDField(required=False, allow_null=True, default=None)

    # Browser fingerprint
    browser_fingerprint = serializers.CharField(
        max_length=64, required=False, allow_blank=True, default=""
    )

    # Extra metadata
    extra = serializers.JSONField(required=False, default=dict)
    project_name = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    environment = serializers.CharField(
        max_length=20, required=False, allow_blank=True, default=""
    )

    def validate_http_status(self, value):
        if value is not None and not (100 <= value <= 599):
            raise serializers.ValidationError("http_status must be between 100 and 599")
        return value


class IngestBatchSerializer(serializers.Serializer):
    """Wraps a list of events. Enforces max batch size."""

    events = serializers.ListField(
        child=FrontendEventIngestSerializer(),
        min_length=1,
        max_length=50,
        error_messages={
            "max_length": "Batch size exceeds maximum of 50 events per request.",
        },
    )
