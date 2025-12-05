"""
Terminal ping command - check if Electron is connected.
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
async def ping(client) -> bool:
    """
    Send ping to terminal.

    Used to check if Electron is connected and responsive.

    Args:
        client: TerminalStreamingCommandClient

    Returns:
        True if sent successfully
    """
    if not PROTO_AVAILABLE:
        logger.error("Proto not available for ping")
        return False

    command = _create_command()
    command.ping.CopyFrom(pb2.PingCommand(
        sequence=int(timezone.now().timestamp())
    ))

    return await client._send_command(command)


@command()
async def ping_sync(client, timeout: float = 5.0):
    """
    Send ping and wait for response (pong).

    Args:
        client: TerminalStreamingCommandClient
        timeout: Timeout in seconds

    Returns:
        CommandAck protobuf with latency info
    """
    if not PROTO_AVAILABLE:
        raise RuntimeError("Proto not available")

    import time
    start = time.time()

    command = _create_command()
    command.ping.CopyFrom(pb2.PingCommand(
        sequence=int(timezone.now().timestamp())
    ))

    ack = await client.send_command_and_wait(command, timeout=timeout)

    # Add latency to response
    latency_ms = (time.time() - start) * 1000
    ack.latency_ms = latency_ms

    return ack
