"""
Activity Serializers

Serializers for activity tracking and quick actions.
"""

from rest_framework import serializers


class QuickActionSerializer(serializers.Serializer):
    """
    Serializer for quick action buttons.

    Maps to QuickAction Pydantic model.
    """

    title = serializers.CharField(help_text="Action title")
    description = serializers.CharField(help_text="Action description")
    icon = serializers.CharField(help_text="Material icon name")
    link = serializers.CharField(help_text="Action URL")
    color = serializers.ChoiceField(
        choices=['primary', 'success', 'warning', 'danger', 'secondary', 'info', 'default'],
        default='primary',
        help_text="Button color theme"
    )
    category = serializers.CharField(default='general', help_text="Action category")


class ActivityEntrySerializer(serializers.Serializer):
    """Serializer for recent activity entries."""

    id = serializers.IntegerField(help_text="Activity ID")
    user = serializers.CharField(help_text="User who performed the action")
    action = serializers.CharField(help_text="Action type (created, updated, deleted, etc.)")
    resource = serializers.CharField(help_text="Resource affected")
    timestamp = serializers.CharField(help_text="Activity timestamp (ISO format)")
    icon = serializers.CharField(help_text="Material icon name")
    color = serializers.CharField(help_text="Icon color")
