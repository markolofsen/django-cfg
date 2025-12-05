"""
Terminal resize command - change terminal dimensions.
"""

import logging
from uuid import uuid4

from django.utils import timezone
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)

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
async def resize_terminal(client, cols: int, rows: int) -> bool:
    """
    Resize terminal.

    Args:
        client: TerminalStreamingCommandClient
        cols: Number of columns
        rows: Number of rows

    Returns:
        True if sent successfully
    """
    if not PROTO_AVAILABLE:
        logger.error("Proto not available for resize_terminal")
        return False

    command = _create_command()
    command.resize.CopyFrom(pb2.ResizeCommand(
        size=pb2.TerminalSize(cols=cols, rows=rows)
    ))

    return await client._send_command(command)


@command()
async def resize_terminal_sync(
    client,
    cols: int,
    rows: int,
    timeout: float = 5.0
):
    """
    Resize terminal and wait for ACK.

    Args:
        client: TerminalStreamingCommandClient
        cols: Number of columns
        rows: Number of rows
        timeout: Timeout in seconds

    Returns:
        CommandAck protobuf
    """
    if not PROTO_AVAILABLE:
        raise RuntimeError("Proto not available")

    command = _create_command()
    command.resize.CopyFrom(pb2.ResizeCommand(
        size=pb2.TerminalSize(cols=cols, rows=rows)
    ))

    return await client.send_command_and_wait(command, timeout=timeout)
