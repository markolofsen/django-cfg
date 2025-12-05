"""
Terminal session commands - start and close session.
"""

import logging
from typing import Optional
from uuid import uuid4

from django.utils import timezone
from google.protobuf.timestamp_pb2 import Timestamp

from apps.terminal.models import TerminalSession

logger = logging.getLogger(__name__)

# Try to import helpers
try:
    from django_cfg.apps.integrations.grpc.services.commands.helpers import (
        command,
        command_with_timestamps,
    )
    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False

    def command(**kwargs):
        def decorator(func):
            return func
        return decorator

    def command_with_timestamps(**kwargs):
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


@command_with_timestamps(
    success_status=TerminalSession.Status.CONNECTED,
    timestamp_field='connected_at'
)
async def start_session(
    client,
    session: TerminalSession,
    shell: Optional[str] = None,
    working_directory: Optional[str] = None,
) -> bool:
    """
    Start terminal session.

    Sends StartSessionCommand to Electron with session configuration.

    Args:
        client: TerminalStreamingCommandClient
        session: TerminalSession model
        shell: Override shell (default: session.shell)
        working_directory: Override working directory

    Returns:
        True if sent successfully
    """
    if not PROTO_AVAILABLE:
        logger.error("Proto not available for start_session")
        return False

    # Build session config
    config = pb2.SessionConfig(
        session_id=str(session.id),
        shell=shell or session.shell,
        working_directory=working_directory or session.working_directory,
    )

    # Add environment variables
    if session.environment:
        for key, value in session.environment.items():
            config.env[key] = str(value)

    command = _create_command()
    command.start_session.CopyFrom(pb2.StartSessionCommand(config=config))

    return await client._send_command(command)


@command_with_timestamps(
    success_status=TerminalSession.Status.DISCONNECTED,
    timestamp_field='disconnected_at'
)
async def close_session(
    client,
    session: TerminalSession,
    reason: str = "",
    force: bool = False,
) -> bool:
    """
    Close terminal session.

    Sends CloseSessionCommand to Electron.

    Args:
        client: TerminalStreamingCommandClient
        session: TerminalSession model
        reason: Reason for closing
        force: Force close (kill processes)

    Returns:
        True if sent successfully
    """
    if not PROTO_AVAILABLE:
        logger.error("Proto not available for close_session")
        return False

    command = _create_command()
    command.close_session.CopyFrom(pb2.CloseSessionCommand(
        reason=reason,
        force=force,
    ))

    return await client._send_command(command)


@command()
async def close_session_sync(
    client,
    session: TerminalSession,
    reason: str = "",
    force: bool = False,
    timeout: float = 10.0,
):
    """
    Close terminal session and wait for ACK.

    Args:
        client: TerminalStreamingCommandClient
        session: TerminalSession model
        reason: Reason for closing
        force: Force close
        timeout: Timeout in seconds

    Returns:
        CommandAck protobuf
    """
    if not PROTO_AVAILABLE:
        raise RuntimeError("Proto not available")

    command = _create_command()
    command.close_session.CopyFrom(pb2.CloseSessionCommand(
        reason=reason,
        force=force,
    ))

    return await client.send_command_and_wait(command, timeout=timeout)
