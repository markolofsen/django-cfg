"""
Terminal input command - send keyboard input to PTY.
"""

import logging
from uuid import uuid4

from django.utils import timezone
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)

# Try to import helpers
try:
    from django_cfg.apps.integrations.grpc.services.commands.helpers import (
        CommandBuilder,
        command,
    )
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


def _create_timestamp():
    """Create protobuf timestamp."""
    ts = Timestamp()
    ts.FromDatetime(timezone.now())
    return ts


def _create_command():
    """Create base DjangoMessage."""
    if not PROTO_AVAILABLE:
        return None

    return pb2.DjangoMessage(
        command_id=str(uuid4()),
        timestamp=_create_timestamp(),
    )


@command()
async def send_input(client, data: bytes) -> bool:
    """
    Send input to terminal.

    Args:
        client: TerminalStreamingCommandClient
        data: Input bytes (keyboard data)

    Returns:
        True if sent successfully
    """
    if not PROTO_AVAILABLE:
        logger.error("Proto not available for send_input")
        return False

    command = _create_command()
    command.input.CopyFrom(pb2.TerminalInput(
        data=data,
        sequence=int(timezone.now().timestamp() * 1000),
    ))

    return await client._send_command(command)


@command()
async def send_input_sync(client, data: bytes, timeout: float = 5.0):
    """
    Send input to terminal and wait for ACK.

    Args:
        client: TerminalStreamingCommandClient
        data: Input bytes
        timeout: Timeout in seconds

    Returns:
        CommandAck protobuf
    """
    if not PROTO_AVAILABLE:
        raise RuntimeError("Proto not available")

    command = _create_command()
    command.input.CopyFrom(pb2.TerminalInput(
        data=data,
        sequence=int(timezone.now().timestamp() * 1000),
    ))

    return await client.send_command_and_wait(command, timeout=timeout)
