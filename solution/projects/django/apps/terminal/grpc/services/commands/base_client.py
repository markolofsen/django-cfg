"""
Terminal Streaming Command Client.

Adapter for sending commands to Electron terminal clients via gRPC.
"""

import logging
from typing import Optional

from apps.terminal.models import TerminalSession

logger = logging.getLogger(__name__)

# Try to import from django-cfg
try:
    from django_cfg.apps.integrations.grpc.services.commands.base import (
        StreamingCommandClient,
    )
    GRPC_COMMANDS_AVAILABLE = True
except ImportError:
    GRPC_COMMANDS_AVAILABLE = False
    StreamingCommandClient = object  # Fallback base class

# Import generated protobuf
try:
    from ..generated import terminal_streaming_service_pb2 as pb2
    from ..generated import terminal_streaming_service_pb2_grpc as pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    pb2 = None
    pb2_grpc = None


class TerminalStreamingCommandClient(StreamingCommandClient if GRPC_COMMANDS_AVAILABLE else object):
    """
    Terminal-specific command client.

    Sends commands to Electron terminal clients via gRPC streaming.

    Inherits from StreamingCommandClient which provides:
    - _send_command() for fire-and-forget commands
    - send_command_and_wait() for synchronous commands with ACK
    - Auto-detection of same-process vs cross-process mode
    """

    if PROTO_AVAILABLE:
        # gRPC service configuration
        stub_class = pb2_grpc.TerminalStreamingServiceStub
        request_class = pb2.SendCommandRequest if hasattr(pb2, 'SendCommandRequest') else None
        rpc_method_name = "SendCommandToBot"  # Fire-and-forget
        _sync_rpc_method_name = "ExecuteCommandSync"  # Wait for ACK
        client_id_field = "session_id"

    def __init__(
        self,
        session_id: str,
        session: Optional[TerminalSession] = None,
        **kwargs
    ):
        """
        Initialize terminal command client.

        Args:
            session_id: Terminal session UUID
            session: Optional TerminalSession model instance
        """
        if GRPC_COMMANDS_AVAILABLE:
            super().__init__(client_id=session_id, **kwargs)
        else:
            self.client_id = session_id

        self.session_id = session_id
        self.session = session

    async def _send_command(self, command) -> bool:
        """
        Send command to terminal (fire-and-forget).

        Args:
            command: DjangoMessage protobuf

        Returns:
            True if command was sent successfully
        """
        if GRPC_COMMANDS_AVAILABLE:
            return await super()._send_command(command)

        # Fallback: use handlers directly
        from ..handlers import get_terminal_service
        service = get_terminal_service()

        if not service:
            logger.warning(f"Terminal service not available for session {self.session_id}")
            return False

        queue = service._sessions.get(self.session_id)
        if not queue:
            logger.warning(f"Session {self.session_id} not connected")
            return False

        await queue.put(command)
        return True

    async def send_command_and_wait(self, command, timeout: float = 5.0):
        """
        Send command and wait for acknowledgment.

        Args:
            command: DjangoMessage protobuf
            timeout: Timeout in seconds

        Returns:
            CommandAck protobuf
        """
        if GRPC_COMMANDS_AVAILABLE:
            return await super().send_command_and_wait(
                command=command,
                timeout=timeout,
                command_id_field="command_id"
            )

        # Fallback: just send and return mock ACK
        success = await self._send_command(command)
        return type('CommandAck', (), {
            'command_id': command.command_id,
            'success': success,
            'message': 'Sent' if success else 'Failed'
        })()


def get_terminal_command_client(
    session_id: str,
    session: Optional[TerminalSession] = None
) -> TerminalStreamingCommandClient:
    """
    Get terminal command client for session.

    Args:
        session_id: Terminal session UUID
        session: Optional TerminalSession model

    Returns:
        TerminalStreamingCommandClient instance
    """
    return TerminalStreamingCommandClient(
        session_id=session_id,
        session=session
    )
