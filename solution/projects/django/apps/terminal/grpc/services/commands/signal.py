"""
Terminal signal command - send signal to PTY process.
"""

import logging
from uuid import uuid4

from django.utils import timezone
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)

# Signal constants
SIGINT = 2    # Ctrl+C
SIGKILL = 9   # Kill
SIGTERM = 15  # Terminate

# Try to import helpers
try:
    from django_cfg.apps.integrations.grpc.services.commands.helpers import command
    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False

    def command():
        def decorator(func):
            return func
        return decorator

# Import protobuf
try:
    from ..generated import terminal_streaming_service_pb2 as pb2
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    pb2 = None


def _create_command():
    """Create base DjangoMessage."""
    if not PROTO_AVAILABLE:
        return None

    ts = Timestamp()
    ts.FromDatetime(timezone.now())

    return pb2.DjangoMessage(
        command_id=str(uuid4()),
        timestamp=ts,
    )


@command()
async def send_signal(client, signal: int = SIGINT) -> bool:
    """
    Send signal to terminal process.

    Args:
        client: TerminalStreamingCommandClient
        signal: Signal number (default: SIGINT=2 for Ctrl+C)

    Returns:
        True if sent successfully
    """
    if not PROTO_AVAILABLE:
        logger.error("Proto not available for send_signal")
        return False

    command = _create_command()
    command.signal.CopyFrom(pb2.SignalCommand(signal=signal))

    return await client._send_command(command)


@command()
async def send_sigint(client) -> bool:
    """Send SIGINT (Ctrl+C) to terminal."""
    return await send_signal(client, SIGINT)


@command()
async def send_sigterm(client) -> bool:
    """Send SIGTERM to terminal."""
    return await send_signal(client, SIGTERM)


@command()
async def send_sigkill(client) -> bool:
    """Send SIGKILL to terminal."""
    return await send_signal(client, SIGKILL)


@command()
async def send_signal_sync(client, signal: int = SIGINT, timeout: float = 5.0):
    """
    Send signal to terminal and wait for ACK.

    Args:
        client: TerminalStreamingCommandClient
        signal: Signal number
        timeout: Timeout in seconds

    Returns:
        CommandAck protobuf
    """
    if not PROTO_AVAILABLE:
        raise RuntimeError("Proto not available")

    command = _create_command()
    command.signal.CopyFrom(pb2.SignalCommand(signal=signal))

    return await client.send_command_and_wait(command, timeout=timeout)
