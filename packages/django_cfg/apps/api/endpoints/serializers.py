"""
Django CFG Endpoints Status Serializers

DRF serializers for endpoints status check API.
"""

from rest_framework import serializers


class EndpointSerializer(serializers.Serializer):
    """Serializer for single endpoint status."""

    url = serializers.CharField(
        help_text="Resolved URL (for parametrized URLs) or URL pattern"
    )
    url_pattern = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Original URL pattern (for parametrized URLs)"
    )
    url_name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Django URL name (if available)"
    )
    namespace = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="URL namespace"
    )
    group = serializers.CharField(
        help_text="URL group (up to 3 depth)"
    )
    view = serializers.CharField(
        required=False,
        help_text="View function/class name"
    )
    status = serializers.CharField(
        help_text="Status: healthy, unhealthy, warning, error, skipped, pending"
    )
    status_code = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="HTTP status code"
    )
    response_time_ms = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Response time in milliseconds"
    )
    is_healthy = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Whether endpoint is healthy"
    )
    error = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Error message if check failed"
    )
    error_type = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Error type: database, general, etc."
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Reason for warning/skip"
    )
    last_checked = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Timestamp of last check"
    )
    has_parameters = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether URL has parameters that were resolved with test values"
    )
    required_auth = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether endpoint required JWT authentication"
    )
    rate_limited = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether endpoint returned 429 (rate limited)"
    )


class EndpointsStatusSerializer(serializers.Serializer):
    """Serializer for overall endpoints status response."""

    status = serializers.CharField(
        help_text="Overall status: healthy, degraded, or unhealthy"
    )
    timestamp = serializers.DateTimeField(
        help_text="Timestamp of the check"
    )
    total_endpoints = serializers.IntegerField(
        help_text="Total number of endpoints checked"
    )
    healthy = serializers.IntegerField(
        help_text="Number of healthy endpoints"
    )
    unhealthy = serializers.IntegerField(
        help_text="Number of unhealthy endpoints"
    )
    warnings = serializers.IntegerField(
        help_text="Number of endpoints with warnings"
    )
    errors = serializers.IntegerField(
        help_text="Number of endpoints with errors"
    )
    skipped = serializers.IntegerField(
        help_text="Number of skipped endpoints"
    )
    endpoints = EndpointSerializer(
        many=True,
        help_text="List of all endpoints with their status"
    )
