"""
Command History Serializers.
"""
from rest_framework import serializers

from apps.terminal.models import CommandHistory


class CommandHistoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for command lists."""

    output_preview = serializers.CharField(read_only=True)
    duration_ms = serializers.IntegerField(read_only=True)
    is_success = serializers.BooleanField(read_only=True)
    session_id = serializers.UUIDField(source='session.id', read_only=True)

    class Meta:
        model = CommandHistory
        fields = [
            'id', 'session_id', 'command', 'status', 'exit_code',
            'output_preview', 'duration_ms', 'is_success', 'created_at'
        ]


class CommandHistoryDetailSerializer(serializers.ModelSerializer):
    """Full serializer for command details."""

    session_id = serializers.UUIDField(source='session.id', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    duration_ms = serializers.IntegerField(read_only=True)
    is_success = serializers.BooleanField(read_only=True)

    class Meta:
        model = CommandHistory
        fields = '__all__'
