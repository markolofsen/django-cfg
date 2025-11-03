"""
Statistics Serializers

Serializers for dashboard statistics endpoints.
"""

from rest_framework import serializers


class StatCardSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics cards.

    Maps to StatCard Pydantic model.
    """

    title = serializers.CharField(help_text="Card title")
    value = serializers.CharField(help_text="Main value to display")
    icon = serializers.CharField(help_text="Material icon name")
    change = serializers.CharField(required=False, allow_null=True, help_text="Change indicator (e.g., '+12%')")
    change_type = serializers.ChoiceField(
        choices=['positive', 'negative', 'neutral'],
        default='neutral',
        help_text="Change type"
    )
    description = serializers.CharField(required=False, allow_null=True, help_text="Additional description")
    color = serializers.CharField(default='primary', help_text="Card color theme")


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics."""

    total_users = serializers.IntegerField(help_text="Total number of users")
    active_users = serializers.IntegerField(help_text="Active users (last 30 days)")
    new_users = serializers.IntegerField(help_text="New users (last 7 days)")
    superusers = serializers.IntegerField(help_text="Number of superusers")


class AppStatisticsSerializer(serializers.Serializer):
    """Serializer for application-specific statistics."""

    app_name = serializers.CharField(help_text="Application name")
    statistics = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Application statistics"
    )
