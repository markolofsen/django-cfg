"""
Command client for sending commands to Electron terminal via streaming.

Maximum decomposition: each command in separate file.

Structure:
- base_client.py: TerminalStreamingCommandClient (extends universal base)
- input.py: send_input()
- resize.py: resize_terminal()
- signal.py: send_signal(), send_sigint(), send_sigterm(), send_sigkill()
- session.py: start_session(), close_session()
- ping.py: ping()

Created: 2025-12-04
Status: %%DEVELOPMENT%%
"""

from django_cfg.apps.integrations.grpc.services.commands.registry import (
    register_streaming_service,
    get_streaming_service,
    list_streaming_services,
)
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder

from .base_client import TerminalStreamingCommandClient
from .input import send_input, send_input_sync
from .resize import resize_terminal, resize_terminal_sync
from .signal import (
    send_signal,
    send_sigint,
    send_sigterm,
    send_sigkill,
    send_signal_sync,
    SIGINT,
    SIGTERM,
    SIGKILL,
)
from .session import start_session, close_session, close_session_sync
from .ping import ping, ping_sync

# Import protobuf types for sync methods
try:
    from ..generated import terminal_streaming_service_pb2 as pb2
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    pb2 = None


class StreamingCommandClient(TerminalStreamingCommandClient):
    """
    Complete streaming command client with all terminal commands.

    Each command is implemented in a separate file for maximum decomposition.

    Extends TerminalStreamingCommandClient with convenient methods.

    Methods come in two flavors:
    1. Async (fire-and-forget): Returns bool (command sent or not)
    2. Sync (wait for response): Returns CommandAck (command result from Electron)
    """

    # ========================================================================
    # Async Commands (fire-and-forget) - return bool
    # ========================================================================

    async def send_input(self, data: bytes) -> bool:
        """Send keyboard input to terminal (async)."""
        return await send_input(self, data)

    async def resize_terminal(self, cols: int, rows: int) -> bool:
        """Resize terminal dimensions (async)."""
        return await resize_terminal(self, cols, rows)

    async def send_signal(self, signal: int = SIGINT) -> bool:
        """Send signal to terminal process (async)."""
        return await send_signal(self, signal)

    async def send_sigint(self) -> bool:
        """Send SIGINT (Ctrl+C) to terminal (async)."""
        return await send_sigint(self)

    async def send_sigterm(self) -> bool:
        """Send SIGTERM to terminal (async)."""
        return await send_sigterm(self)

    async def send_sigkill(self) -> bool:
        """Send SIGKILL to terminal (async)."""
        return await send_sigkill(self)

    async def start_session(
        self,
        shell: str = None,
        working_directory: str = None,
    ) -> bool:
        """Start terminal session (async)."""
        return await start_session(self, self.session, shell, working_directory)

    async def close_session(self, reason: str = "", force: bool = False) -> bool:
        """Close terminal session (async)."""
        return await close_session(self, self.session, reason, force)

    async def ping(self) -> bool:
        """Send ping to check if Electron is connected (async)."""
        return await ping(self)

    # ========================================================================
    # Sync Commands (wait for response) - return CommandAck
    # ========================================================================

    async def send_input_sync(self, data: bytes, timeout: float = 5.0):
        """Send keyboard input and wait for ACK."""
        return await send_input_sync(self, data, timeout)

    async def resize_terminal_sync(self, cols: int, rows: int, timeout: float = 5.0):
        """Resize terminal and wait for ACK."""
        return await resize_terminal_sync(self, cols, rows, timeout)

    async def send_signal_sync(self, signal: int = SIGINT, timeout: float = 5.0):
        """Send signal and wait for ACK."""
        return await send_signal_sync(self, signal, timeout)

    async def close_session_sync(
        self,
        reason: str = "",
        force: bool = False,
        timeout: float = 10.0,
    ):
        """Close terminal session and wait for ACK."""
        return await close_session_sync(self, self.session, reason, force, timeout)

    async def ping_sync(self, timeout: float = 5.0):
        """Send ping and wait for pong with latency info."""
        return await ping_sync(self, timeout)


__all__ = [
    'StreamingCommandClient',
    'TerminalStreamingCommandClient',
    # Registry (from universal solution)
    'register_streaming_service',
    'get_streaming_service',
    'list_streaming_services',
    # Signals
    'SIGINT',
    'SIGTERM',
    'SIGKILL',
]
