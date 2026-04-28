"""
django_monitor.api.serializers — DRF serializers for the ingest endpoint.

No ORM models — fields mirror FrontendEventSyncData exactly.
"""

from __future__ import annotations

from django.db import models
from rest_framework import serializers


class FrontendEventType(models.TextChoices):
    """Named enum so drf-spectacular emits a standalone components/schemas
    entry — Hey API then materializes it as a TS `enum` (not an inline union)."""

    JS_ERROR = "JS_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    ERROR = "ERROR"
    WARNING = "WARNING"
    PAGE_VIEW = "PAGE_VIEW"
    PERFORMANCE = "PERFORMANCE"
    CONSOLE = "CONSOLE"


class FrontendEventLevel(models.TextChoices):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class FrontendEventIngestSerializer(serializers.Serializer):
    """Single browser event payload."""

    # Required
    event_type = serializers.ChoiceField(choices=FrontendEventType.choices)
    message = serializers.CharField(max_length=5000)

    # Optional core
    level = serializers.ChoiceField(
        choices=FrontendEventLevel.choices,
        default=FrontendEventLevel.ERROR,
        required=False,
    )
    stack_trace = serializers.CharField(max_length=10000, required=False, allow_blank=True, default="")
    url = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    fingerprint = serializers.CharField(max_length=64, required=False, allow_blank=True, default="")

    # Network context
    http_status = serializers.IntegerField(required=False, allow_null=True, default=None)
    http_method = serializers.CharField(max_length=10, required=False, allow_blank=True, default="")
    http_url = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")

    # Client context
    session_id = serializers.CharField(max_length=64, required=False, allow_blank=True, default="")
    user_agent = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
    build_id = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    environment = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")

    # Extra
    extra = serializers.JSONField(required=False, default=dict)
    project_name = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")


class IngestBatchSerializer(serializers.Serializer):
    """Batch of up to 50 browser events."""

    events = serializers.ListField(
        child=FrontendEventIngestSerializer(),
        max_length=25,
        min_length=1,
    )
