"""
Overview Serializers

Serializers for dashboard overview endpoint.
"""

from rest_framework import serializers


class DashboardOverviewSerializer(serializers.Serializer):
    """
    Main serializer for dashboard overview endpoint.
    Uses DictField to avoid allOf generation in OpenAPI.
    """

    stat_cards = serializers.ListField(
        child=serializers.DictField(),
        help_text="Dashboard statistics cards"
    )
    system_health = serializers.ListField(
        child=serializers.DictField(),
        help_text="System health status"
    )
    quick_actions = serializers.ListField(
        child=serializers.DictField(),
        help_text="Quick action buttons"
    )
    recent_activity = serializers.ListField(
        child=serializers.DictField(),
        help_text="Recent activity entries"
    )
    system_metrics = serializers.DictField(help_text="System performance metrics")
    user_statistics = serializers.DictField(help_text="User statistics")
    timestamp = serializers.CharField(help_text="Data timestamp (ISO format)")
