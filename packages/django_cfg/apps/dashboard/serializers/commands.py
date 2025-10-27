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


class CommandsSummarySerializer(serializers.Serializer):
    """Commands summary serializer."""
    total_commands = serializers.IntegerField()
    core_commands = serializers.IntegerField()
    custom_commands = serializers.IntegerField()
    categories = serializers.ListField(child=serializers.CharField())
    commands = CommandSerializer(many=True)
    categorized = serializers.DictField()
