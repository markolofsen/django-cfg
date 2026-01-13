"""
Overview Serializers

Serializers for dashboard overview endpoint.
"""

from rest_framework import serializers
from .statistics import StatCardSerializer, UserStatisticsSerializer, AppStatisticsSerializer
from .system import SystemHealthSerializer, SystemMetricsSerializer
from .activity import QuickActionSerializer, ActivityEntrySerializer


class ExtensionInfoSerializer(serializers.Serializer):
    """Extension information for frontend menu filtering."""
    name = serializers.CharField(help_text="Extension name (e.g., 'support', 'leads')")
    type = serializers.CharField(help_text="Extension type: 'app' or 'module'")
    version = serializers.CharField(allow_null=True, help_text="Extension version")
    is_valid = serializers.BooleanField(help_text="Whether extension is properly configured")
    description = serializers.CharField(allow_null=True, help_text="Extension description")


class DashboardOverviewSerializer(serializers.Serializer):
    """
    Main serializer for dashboard overview endpoint.
    Uses typed serializers for proper OpenAPI schema generation.
    """

    stat_cards = StatCardSerializer(
        many=True,
        help_text="Dashboard statistics cards"
    )
    system_health = SystemHealthSerializer(
        help_text="System health status"
    )
    quick_actions = QuickActionSerializer(
        many=True,
        help_text="Quick action buttons"
    )
    recent_activity = ActivityEntrySerializer(
        many=True,
        help_text="Recent activity entries"
    )
    system_metrics = SystemMetricsSerializer(
        help_text="System performance metrics"
    )
    user_statistics = UserStatisticsSerializer(
        help_text="User statistics"
    )
    app_statistics = AppStatisticsSerializer(
        many=True,
        required=False,
        help_text="Application statistics"
    )
    extensions = ExtensionInfoSerializer(
        many=True,
        required=False,
        help_text="Installed extensions info for menu filtering"
    )
    timestamp = serializers.CharField(help_text="Data timestamp (ISO format)")
