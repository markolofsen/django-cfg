"""
Metrics Serializers

Serializers for universal metrics API.
Supports multiple metric categories with consistent structure.
"""

from rest_framework import serializers


class MetricItemSerializer(serializers.Serializer):
    """
    Individual metric item serializer.

    Flexible structure supporting different metric types.
    """
    # Common fields
    status = serializers.CharField(required=False, allow_null=True)
    status_level = serializers.CharField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_null=True)

    # Allow additional dynamic fields
    class Meta:
        # Accept all additional fields
        extra_kwargs = {'*': {'required': False}}

    def to_representation(self, instance):
        """
        Allow passing through all fields from dict.

        This enables flexible metric items with provider-specific fields.
        """
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)


class MetricCategorySerializer(serializers.Serializer):
    """
    Metric category serializer.

    Groups related metrics (e.g., LLM balances, system health).
    """
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    status = serializers.CharField()
    error = serializers.CharField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_null=True)
    items = MetricItemSerializer(many=True)
    summary = serializers.DictField(required=False)


class MetricsResponseSerializer(serializers.Serializer):
    """
    Complete metrics API response serializer.

    Root response containing all metric categories.
    """
    categories = serializers.DictField(
        child=MetricCategorySerializer(),
        help_text="Metric categories (llm_balances, system_health, etc.)"
    )
    metadata = serializers.DictField(
        help_text="Response metadata (timestamp, counts, etc.)"
    )
