"""
Terminal Session Serializers.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.terminal.models import TerminalSession
from .command_serializers import CommandHistoryListSerializer


class TerminalSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for session lists."""

    is_alive = serializers.BooleanField(read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = TerminalSession
        fields = [
            'id', 'name', 'status', 'display_name', 'is_alive',
            'electron_hostname', 'working_directory', 'shell',
            'connected_at', 'last_heartbeat_at', 'created_at'
        ]


class TerminalSessionDetailSerializer(serializers.ModelSerializer):
    """Full serializer for session details."""

    is_alive = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    heartbeat_age_seconds = serializers.FloatField(read_only=True)
    recent_commands = serializers.SerializerMethodField()

    class Meta:
        model = TerminalSession
        fields = '__all__'
        read_only_fields = [
            'id', 'user', 'status', 'electron_hostname', 'electron_version',
            'commands_count', 'bytes_sent', 'bytes_received',
            'connected_at', 'last_heartbeat_at', 'disconnected_at',
            'created_at', 'updated_at'
        ]

    @extend_schema_field(CommandHistoryListSerializer(many=True))
    def get_recent_commands(self, obj):
        """Get last 5 commands for this session."""
        commands = obj.commands.order_by('-created_at')[:5]
        return CommandHistoryListSerializer(commands, many=True).data


class TerminalSessionCreateSerializer(serializers.Serializer):
    """Serializer for creating new session."""

    name = serializers.CharField(max_length=100, required=False, default='')
    shell = serializers.CharField(max_length=50, default='/bin/zsh')
    working_directory = serializers.CharField(max_length=500, default='~')
    environment = serializers.JSONField(required=False, default=dict)


class TerminalInputSerializer(serializers.Serializer):
    """Serializer for sending input."""

    data = serializers.CharField(
        required=False,
        help_text="Input data as string"
    )
    data_base64 = serializers.CharField(
        required=False,
        help_text="Base64 encoded input data"
    )

    def validate(self, attrs):
        if not attrs.get('data') and not attrs.get('data_base64'):
            raise serializers.ValidationError(
                "Either 'data' or 'data_base64' is required"
            )
        return attrs


class TerminalResizeSerializer(serializers.Serializer):
    """Serializer for resize command."""

    cols = serializers.IntegerField(min_value=1, max_value=500)
    rows = serializers.IntegerField(min_value=1, max_value=200)
    width = serializers.IntegerField(required=False, min_value=1)
    height = serializers.IntegerField(required=False, min_value=1)


class TerminalSignalSerializer(serializers.Serializer):
    """Serializer for signal command."""

    SIGNAL_CHOICES = [
        (2, 'SIGINT'),
        (9, 'SIGKILL'),
        (15, 'SIGTERM'),
    ]

    signal = serializers.ChoiceField(choices=SIGNAL_CHOICES)
