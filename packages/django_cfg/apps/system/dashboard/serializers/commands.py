"""
Commands Serializers

Serializers for Django management commands endpoints.
"""

from rest_framework import serializers


class CommandSerializer(serializers.Serializer):
    """Django management command serializer."""
    name = serializers.CharField()
    app = serializers.CharField()
    help = serializers.CharField()
    is_core = serializers.BooleanField()
    is_custom = serializers.BooleanField()
    is_allowed = serializers.BooleanField(required=False)
    risk_level = serializers.CharField(required=False)


class CommandsSummarySerializer(serializers.Serializer):
    """Commands summary serializer."""
    total_commands = serializers.IntegerField()
    core_commands = serializers.IntegerField()
    custom_commands = serializers.IntegerField()
    categories = serializers.ListField(child=serializers.CharField())
    commands = CommandSerializer(many=True)
    categorized = serializers.DictField()


class CommandExecuteRequestSerializer(serializers.Serializer):
    """Request serializer for command execution."""
    command = serializers.CharField(help_text="Name of the Django management command")
    args = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="Positional arguments for the command"
    )
    options = serializers.DictField(
        required=False,
        default=dict,
        help_text="Named options for the command (e.g., {'verbosity': '2'})"
    )


class CommandHelpResponseSerializer(serializers.Serializer):
    """Response serializer for command help."""
    status = serializers.CharField()
    command = serializers.CharField()
    app = serializers.CharField(required=False)
    help_text = serializers.CharField(required=False)
    is_allowed = serializers.BooleanField(required=False)
    risk_level = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
