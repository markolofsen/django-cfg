"""
Command client for sending commands to crypto clients via streaming.

Maximum decomposition: each command in separate file.

Based on universal StreamingCommandClient from django-cfg.

Structure:
- base_client.py: CryptoStreamingCommandClient (extends universal base)
- pause.py: pause_client()
- resume.py: resume_client()
- ping.py: ping_client()
- sync_wallets.py: sync_wallets()
- request_status.py: request_status()

Created: 2025-11-14
Based on: /apps/signals/grpc/services/commands/
Status: %%PRODUCTION%%
"""

from django_cfg.apps.integrations.grpc.services.commands.registry import (
    register_streaming_service,
    get_streaming_service,
    list_streaming_services,
)
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder

from .base_client import CryptoStreamingCommandClient
from .pause import pause_client
from .resume import resume_client
from .ping import ping_client
from .sync_wallets import sync_wallets
from .request_status import request_status

# Import protobuf types once for all sync methods
from ..generated import crypto_streaming_pb2 as pb2
from ..proto.converters import ProtobufConverter


class StreamingCommandClient(CryptoStreamingCommandClient):
    """
    Complete streaming command client with all commands.

    Each command is implemented in a separate file for maximum decomposition.

    Extends universal CryptoStreamingCommandClient with convenient methods.

    Methods come in two flavors:
    1. Async (fire-and-forget): Returns bool (command sent or not)
    2. Sync (wait for response): Returns CommandAck (command result from client)
    """

    # ========================================================================
    # Async Commands (fire-and-forget) - return bool
    # ========================================================================

    async def pause_client(self, reason: str = None) -> bool:
        """Send Pause command (async)."""
        return await pause_client(self, self.client, reason)

    async def resume_client(self, message: str = None) -> bool:
        """Send Resume command (async)."""
        return await resume_client(self, self.client, message)

    async def ping_client(self, sequence: int = 1) -> bool:
        """Send Ping command (async)."""
        return await ping_client(self, self.client, sequence)

    async def sync_wallets(self, symbols: list = None) -> bool:
        """Send SyncWallets command (async)."""
        return await sync_wallets(self, self.client, symbols)

    async def request_status(self, include_stats: bool = False) -> bool:
        """Send RequestStatus command (async)."""
        return await request_status(self, self.client, include_stats)

    # ========================================================================
    # Sync Commands (wait for response) - return CommandAck
    # ========================================================================

    async def _build_and_send_sync(
        self,
        command_field: str,
        command_proto,
        timeout: float
    ):
        """
        Helper: build command and send synchronously (wait for ack).

        Args:
            command_field: Field name in DjangoCommand (e.g., "pause", "resume")
            command_proto: Protobuf command instance (e.g., pb2.PauseClientCommand())
            timeout: Timeout in seconds

        Returns:
            CommandAck protobuf with execution result
        """
        command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
        getattr(command, command_field).CopyFrom(command_proto)
        return await self.send_command_and_wait(command, timeout=timeout)

    async def pause_client_sync(self, reason: str = None, timeout: float = 5.0):
        """Send Pause command and wait for CommandAck response."""
        return await self._build_and_send_sync(
            'pause',
            pb2.PauseClientCommand(reason=reason or "Paused by admin"),
            timeout
        )

    async def resume_client_sync(self, message: str = None, timeout: float = 5.0):
        """Send Resume command and wait for CommandAck response."""
        return await self._build_and_send_sync(
            'resume',
            pb2.ResumeClientCommand(message=message or "Resumed by admin"),
            timeout
        )

    async def ping_client_sync(self, sequence: int = 1, timeout: float = 5.0):
        """Send Ping command and wait for CommandAck response."""
        return await self._build_and_send_sync(
            'ping',
            pb2.PingCommand(sequence=sequence),
            timeout
        )

    async def sync_wallets_sync(self, symbols: list = None, timeout: float = 10.0):
        """Send SyncWallets command and wait for CommandAck response."""
        return await self._build_and_send_sync(
            'sync_wallets',
            pb2.SyncWalletsCommand(symbols=symbols or []),
            timeout
        )

    async def request_status_sync(self, include_stats: bool = False, timeout: float = 5.0):
        """Send RequestStatus command and wait for CommandAck response."""
        return await self._build_and_send_sync(
            'request_status',
            pb2.RequestStatusCommand(include_stats=include_stats),
            timeout
        )


__all__ = [
    'StreamingCommandClient',
    'CryptoStreamingCommandClient',
    'pause_client',
    'resume_client',
    'ping_client',
    'sync_wallets',
    'request_status',
    'register_streaming_service',
    'get_streaming_service',
    'list_streaming_services',
    'CommandBuilder',
]
