"""
Handle Electron client registration.

Based on stockapis pattern - auto-creates session if not found.
"""

import uuid
import asyncio
import logging
from django.utils import timezone

from apps.terminal.models import TerminalSession

logger = logging.getLogger(__name__)


async def handle_registration(
    session_id: str,
    register,  # pb2.RegisterRequest
    output_queue: asyncio.Queue,
    pb2,  # terminal_streaming_service_pb2 module
    common_pb2,  # common_pb2 module (contains SessionConfig)
) -> bool:
    """
    Handle Electron client registration.

    Auto-creates session if not found, or updates existing session.
    Sends StartSessionCommand to Electron via output_queue.

    Args:
        session_id: UUID of the terminal session
        register: RegisterRequest protobuf message
        output_queue: Queue for sending commands back to Electron
        pb2: Protobuf module for creating messages (terminal_streaming_service_pb2)
        common_pb2: Common protobuf module (contains SessionConfig, TerminalSize)

    Returns:
        True if registration successful
    """
    logger.info("=" * 80)
    logger.info(f"📝 TERMINAL REGISTRATION")
    logger.info(f"   Session ID: {session_id[:8]}...")
    logger.info(f"   Hostname: {register.hostname}")
    logger.info(f"   Version: {register.version}")
    logger.info(f"   Platform: {register.platform}")
    logger.info(f"   Shells: {', '.join(register.supported_shells)}")

    try:
        # Validate registration request
        if not register.hostname:
            raise ValueError("Hostname required for registration")

        # Check if session already exists
        try:
            session = await TerminalSession.objects.aget(id=uuid.UUID(session_id))
            # Session exists - update heartbeat and status
            session.electron_hostname = register.hostname
            session.electron_version = register.version
            session.status = TerminalSession.Status.CONNECTED
            session.connected_at = timezone.now()
            session.last_heartbeat_at = timezone.now()
            await session.asave(update_fields=[
                'electron_hostname',
                'electron_version',
                'status',
                'connected_at',
                'last_heartbeat_at',
                'updated_at',
            ])
            created = False
            logger.info(f"♻️  Session re-registered (status: {session.status})")

        except TerminalSession.DoesNotExist:
            # Brand new session - create
            # Determine shell from client's supported shells or use default
            shell = register.supported_shells[0] if register.supported_shells else '/bin/zsh'

            session = await TerminalSession.objects.acreate(
                id=uuid.UUID(session_id),
                electron_hostname=register.hostname,
                electron_version=register.version,
                shell=shell,
                working_directory='~',
                status=TerminalSession.Status.CONNECTED,
                connected_at=timezone.now(),
                last_heartbeat_at=timezone.now(),
            )
            created = True
            logger.info(f"🆕 New session created: {session_id[:8]}...")

        action = "created" if created else "updated"
        logger.info(f"✅ Session {action}: {session_id[:8]}...")

        # Send start session command
        from google.protobuf.timestamp_pb2 import Timestamp
        ts = Timestamp()
        ts.FromDatetime(timezone.now())

        start_command = pb2.DjangoMessage(
            command_id=str(uuid.uuid4()),
            timestamp=ts,
        )

        # Build session config (SessionConfig is in common_pb2)
        session_config = common_pb2.SessionConfig(
            session_id=session_id,
            shell=session.shell,
            working_directory=session.working_directory,
        )

        # Add environment variables if any
        if session.environment:
            for key, value in session.environment.items():
                session_config.env[key] = str(value)

        start_command.start_session.CopyFrom(
            pb2.StartSessionCommand(config=session_config)
        )

        await output_queue.put(start_command)
        logger.info(f"📤 Sent StartSessionCommand to session {session_id[:8]}...")

        logger.info("=" * 80)
        return True

    except Exception as e:
        logger.error(f"❌ Registration error for session {session_id}: {e}", exc_info=True)
        return False
