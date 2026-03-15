"""
DRF serializers for gRPC API Keys.

Read-only serializers for listing and viewing API keys.
Create/Update/Delete operations handled through Django Admin.
"""

from rest_framework import serializers


class ApiKeySerializer(serializers.Serializer):
    """API Key information (read-only)."""

    id = serializers.IntegerField(help_text="Database ID")
    name = serializers.CharField(help_text="Key name/description")
    masked_key = serializers.CharField(help_text="Masked API key (first 4 and last 4 chars)")
    is_active = serializers.BooleanField(help_text="Whether key is active")
    is_valid = serializers.BooleanField(help_text="Whether key is valid (active and not expired)")
    user_id = serializers.IntegerField(help_text="User ID")
    username = serializers.CharField(help_text="Username")
    user_email = serializers.CharField(help_text="User email", allow_blank=True)
    request_count = serializers.IntegerField(help_text="Total requests made with this key")
    last_used_at = serializers.DateTimeField(
        allow_null=True,
        help_text="When key was last used"
    )
    expires_at = serializers.DateTimeField(
        allow_null=True,
        help_text="When key expires (null = never)"
    )
    created_at = serializers.DateTimeField(help_text="When key was created")


class ApiKeyListSerializer(serializers.Serializer):
    """List of API keys response."""

    results = ApiKeySerializer(many=True, help_text="List of API keys")
    count = serializers.IntegerField(help_text="Total number of API keys")


class ApiKeyStatsSerializer(serializers.Serializer):
    """API Key usage statistics."""

    total_keys = serializers.IntegerField(help_text="Total API keys")
    active_keys = serializers.IntegerField(help_text="Active API keys")
    expired_keys = serializers.IntegerField(help_text="Expired API keys")
    total_requests = serializers.IntegerField(help_text="Total requests across all keys")


__all__ = [
    "ApiKeySerializer",
    "ApiKeyListSerializer",
    "ApiKeyStatsSerializer",
]
