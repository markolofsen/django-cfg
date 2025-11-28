"""DRF Serializers for Crypto Client Commands (virtual model)."""
from rest_framework import serializers


class ClientCommandSerializer(serializers.Serializer):
    """
    Virtual serializer for Crypto Client Command interface.

    Clients are not stored in database - they exist as gRPC connections.
    This serializer represents a connected crypto client with its metadata.
    """

    client_id = serializers.CharField(read_only=True, help_text="Client UUID")
    client_name = serializers.CharField(read_only=True, help_text="Client name (e.g., crypto-bot-001)")
    connected = serializers.BooleanField(read_only=True, help_text="Is client currently connected")
    last_heartbeat = serializers.DateTimeField(read_only=True, allow_null=True, help_text="Last heartbeat timestamp")

    # Connection metadata
    metadata = serializers.JSONField(read_only=True, default=dict, help_text="Client metadata")

    # Stats from client
    wallets_synced = serializers.IntegerField(read_only=True, default=0)
    sync_requests = serializers.IntegerField(read_only=True, default=0)
    last_sync = serializers.DateTimeField(read_only=True, allow_null=True, help_text="Last wallet sync timestamp")

    class Meta:
        fields = [
            'client_id',
            'client_name',
            'connected',
            'last_heartbeat',
            'metadata',
            'wallets_synced',
            'sync_requests',
            'last_sync',
        ]


class ClientCommandListSerializer(serializers.Serializer):
    """Lightweight serializer for listing crypto clients."""

    client_id = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    connected = serializers.BooleanField(read_only=True)
    wallets_synced = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        fields = ['client_id', 'client_name', 'connected', 'wallets_synced']
