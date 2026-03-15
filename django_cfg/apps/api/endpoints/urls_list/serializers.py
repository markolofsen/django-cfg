"""
Django CFG URLs List Serializers

DRF serializers for URLs list API.
"""

from rest_framework import serializers


class URLPatternSerializer(serializers.Serializer):
    """Serializer for single URL pattern."""

    pattern = serializers.CharField(
        help_text="URL pattern (e.g., ^api/users/(?P<pk>[^/.]+)/$)"
    )
    name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="URL name (if defined)"
    )
    full_name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Full URL name with namespace (e.g., admin:index)"
    )
    namespace = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="URL namespace"
    )
    view = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="View function/class name"
    )
    view_class = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="View class name (for CBV/ViewSets)"
    )
    methods = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Allowed HTTP methods"
    )
    module = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="View module path"
    )


class URLsListSerializer(serializers.Serializer):
    """Serializer for URLs list response."""

    status = serializers.CharField(
        help_text="Status: success or error"
    )
    service = serializers.CharField(
        help_text="Service name"
    )
    version = serializers.CharField(
        help_text="Django-CFG version"
    )
    base_url = serializers.CharField(
        help_text="Base URL of the service"
    )
    total_urls = serializers.IntegerField(
        help_text="Total number of registered URLs"
    )
    urls = URLPatternSerializer(
        many=True,
        help_text="List of all registered URL patterns"
    )
