"""
Base Serializers

Common serializers used across dashboard endpoints.
"""

from rest_framework import serializers


class APIResponseSerializer(serializers.Serializer):
    """Standard API response wrapper."""

    success = serializers.BooleanField(help_text="Operation success status")
    message = serializers.CharField(required=False, help_text="Success message")
    error = serializers.CharField(required=False, help_text="Error message")
    data = serializers.DictField(required=False, help_text="Response data")
