"""
Terminal gRPC Streaming Service.

Main service implementation for bidirectional terminal I/O.
"""

import uuid
import asyncio
import logging
from typing import AsyncIterator, Dict, Optional

import grpc
from django.utils import timezone
from google.protobuf.timestamp_pb2 import Timestamp

from apps.terminal.models import TerminalSession
from .registration import handle_registration
from .output import handle_terminal_output
from .status import handle_status_update
from .error import handle_error_report

# Import commands for creating protobuf messages
from ..commands import (
    StreamingCommandClient,
    SIGINT,
)

logger = logging.getLogger(__name__)

# Import generated protobuf modules
try:
    from ..generated import terminal_streaming_service_pb2 as pb2
    from ..generated import terminal_streaming_service_pb2_grpc as pb2_grpc
    from ..generated import common_pb2
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    pb2 = None
    pb2_grpc = None
    common_pb2 = None
    logger.warning(
        "Terminal proto files not generated. "
        "Run: ./apps/terminal/grpc/services/proto/generate_proto.sh"
    )


class TerminalStreamingServiceServicer:
    """
    Terminal bidirectional streaming service.

    Handles communication between Django and Electron for terminal I/O.
    """

    def __init__(self):
        # Active sessions: session_id -> output_queue
        self._sessions: Dict[str, asyncio.Queue] = {}
        # WebSocket manager (injected)
        self._websocket_manager = None

    def set_websocket_manager(self, manager) -> None:
        """Set WebSocket manager for forwarding output to browser."""
        self._websocket_manager = manager

    async def ConnectTerminal(
        self,
        request_iterator: AsyncIterator,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator:
        """
        Bidirectional streaming for terminal I/O.

        Electron opens stream -> Django sends input -> Electron sends output.
        """
        if not PROTO_AVAILABLE:
            await context.abort(
                grpc.StatusCode.UNAVAILABLE,
                "Proto files not generated"
            )
            return

        session_id: Optional[str] = None
        output_queue: asyncio.Queue = asyncio.Queue()

        async def process_messages():
            """Process incoming messages from Electron."""
            nonlocal session_id

            try:
                async for message in request_iterator:
                    session_id = message.session_id
                    payload_type = message.WhichOneof('payload')

                    logger.debug(
                        f"Received {payload_type} from session {session_id[:8]}..."
                    )

                    if payload_type == 'register':
                        success = await handle_registration(
                            session_id,
                            message.register,
                            output_queue,
                            pb2,
                            common_pb2,
                        )
                        if success:
                            self._sessions[session_id] = output_queue

                    elif payload_type == 'output':
                        await handle_terminal_output(
                            session_id,
                            message.output,
                            self._websocket_manager,
                        )

                    elif payload_type == 'heartbeat':
                        await self._handle_heartbeat(session_id)

                    elif payload_type == 'status':
                        await handle_status_update(session_id, message.status)

                    elif payload_type == 'error':
                        await handle_error_report(session_id, message.error)

                    elif payload_type == 'ack':
                        logger.debug(
                            f"CommandAck: {message.ack.command_id} "
                            f"success={message.ack.success}"
                        )

                    elif payload_type == 'command_complete':
                        await self._handle_command_complete(
                            session_id,
                            message.command_complete,
                        )

            except asyncio.CancelledError:
                logger.info(f"Message processing cancelled for {session_id}")
            except Exception as e:
                logger.error(f"Error processing messages: {e}", exc_info=True)

        # Start processing in background
        process_task = asyncio.create_task(process_messages())

        try:
            # Yield commands from queue
            while True:
                try:
                    command = await asyncio.wait_for(
                        output_queue.get(),
                        timeout=60.0  # Check every minute
                    )
                    yield command
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    if session_id:
                        ping = self._create_ping()
                        yield ping

        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
        finally:
            process_task.cancel()
            if session_id:
                self._sessions.pop(session_id, None)
                # Update session status
                try:
                    await TerminalSession.objects.filter(
                        id=uuid.UUID(session_id)
                    ).aupdate(
                        status=TerminalSession.Status.DISCONNECTED,
                        disconnected_at=timezone.now(),
                    )
                except Exception:
                    pass

    async def _handle_heartbeat(self, session_id: str) -> None:
        """Update session heartbeat timestamp."""
        try:
            await TerminalSession.objects.filter(
                id=uuid.UUID(session_id)
            ).aupdate(last_heartbeat_at=timezone.now())
        except Exception as e:
            logger.error(f"Heartbeat update failed: {e}")

    async def _handle_command_complete(
        self,
        session_id: str,
        complete,  # pb2.CommandComplete
    ) -> None:
        """Handle command completion notification."""
        from django.db.models import F

        logger.info(
            f"Command complete: session={session_id[:8]}... "
            f"exit_code={complete.exit_code} duration={complete.duration_ms}ms"
        )

        # Increment commands count
        await TerminalSession.objects.filter(
            id=uuid.UUID(session_id)
        ).aupdate(commands_count=F('commands_count') + 1)

    def _create_ping(self):
        """Create ping command using command builder."""
        from ..commands.ping import _create_command as create_ping_command

        command = create_ping_command()
        if command:
            command.ping.CopyFrom(pb2.PingCommand(sequence=int(timezone.now().timestamp())))
        return command

    def _get_command_client(self, session_id: str) -> Optional["_ServicerCommandClient"]:
        """
        Get command client adapter for session.

        Returns a client that sends commands to the session's queue.
        """
        queue = self._sessions.get(session_id)
        if not queue:
            logger.warning(f"Session not found: {session_id}")
            return None

        return _ServicerCommandClient(session_id, queue)

    async def send_input(self, session_id: str, data: bytes) -> bool:
        """
        Send input to terminal session.

        Called from Centrifugo RPC handler to forward keyboard input.
        """
        client = self._get_command_client(session_id)
        if not client:
            return False

        from ..commands.input import send_input
        return await send_input(client, data)

    async def send_resize(
        self,
        session_id: str,
        cols: int,
        rows: int,
    ) -> bool:
        """Send resize command to terminal session."""
        client = self._get_command_client(session_id)
        if not client:
            return False

        from ..commands.resize import resize_terminal
        return await resize_terminal(client, cols, rows)

    async def send_signal(self, session_id: str, signal: int = SIGINT) -> bool:
        """Send signal to terminal session (e.g., SIGINT=2)."""
        client = self._get_command_client(session_id)
        if not client:
            return False

        from ..commands.signal import send_signal
        return await send_signal(client, signal)

    async def close_session(self, session_id: str, reason: str = "") -> bool:
        """Close terminal session."""
        client = self._get_command_client(session_id)
        if not client:
            return False

        # Get session model for close command
        try:
            session = await TerminalSession.objects.aget(id=uuid.UUID(session_id))
        except TerminalSession.DoesNotExist:
            return False

        from ..commands.session import close_session
        return await close_session(client, session, reason, force=False)

    # RPC methods (non-streaming)

    async def CreateSession(self, request, context):
        """Create new terminal session."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = await User.objects.aget(id=request.user_id)

            session = await TerminalSession.objects.acreate(
                user=user,
                name=request.name or "",
                shell=request.config.shell or "/bin/zsh",
                working_directory=request.config.working_directory or "~",
                environment=dict(request.config.env) if request.config.env else {},
            )

            return pb2.CreateSessionResponse(
                success=True,
                session_id=str(session.id),
            )

        except User.DoesNotExist:
            return pb2.CreateSessionResponse(
                success=False,
                error="User not found",
            )
        except Exception as e:
            return pb2.CreateSessionResponse(
                success=False,
                error=str(e),
            )

    async def CloseSession(self, request, context):
        """Close terminal session."""
        try:
            session_id = request.session_id
            await self.close_session(session_id, request.reason)

            await TerminalSession.objects.filter(
                id=uuid.UUID(session_id)
            ).aupdate(
                status=TerminalSession.Status.DISCONNECTED,
                disconnected_at=timezone.now(),
            )

            return pb2.CloseSessionResponse(success=True)

        except Exception as e:
            return pb2.CloseSessionResponse(success=False, error=str(e))

    async def GetSessionStatus(self, request, context):
        """Get terminal session status."""
        try:
            session = await TerminalSession.objects.aget(
                id=uuid.UUID(request.session_id)
            )

            # Map Django status to proto status
            status_map = {
                TerminalSession.Status.PENDING: 1,
                TerminalSession.Status.CONNECTED: 2,
                TerminalSession.Status.DISCONNECTED: 3,
                TerminalSession.Status.ERROR: 4,
            }

            connected_at = None
            if session.connected_at:
                connected_at = Timestamp()
                connected_at.FromDatetime(session.connected_at)

            last_heartbeat = None
            if session.last_heartbeat_at:
                last_heartbeat = Timestamp()
                last_heartbeat.FromDatetime(session.last_heartbeat_at)

            return pb2.GetSessionStatusResponse(
                exists=True,
                status=status_map.get(session.status, 0),
                electron_hostname=session.electron_hostname or "",
                connected_at=connected_at,
                last_heartbeat_at=last_heartbeat,
                commands_count=session.commands_count,
            )

        except TerminalSession.DoesNotExist:
            return pb2.GetSessionStatusResponse(exists=False)

    async def HealthCheck(self, request, context):
        """Health check endpoint."""
        active_sessions = len(self._sessions)

        return pb2.HealthCheckResponse(
            healthy=True,
            version="1.0.0",
            active_sessions=active_sessions,
            connected_clients=active_sessions,
        )

    # ========================================================================
    # Terminal Control RPC Methods (for external clients)
    # ========================================================================

    async def SendInput(self, request, context):
        """
        Send input to terminal session via unary RPC.

        Used by management commands and other clients to send input.
        """
        session_id = request.session_id
        data = request.data

        logger.info(f"📥 SendInput RPC: session={session_id[:8]}..., bytes={len(data)}")

        success = await self.send_input(session_id, data)

        if success:
            return pb2.SendInputResponse(success=True)
        else:
            return pb2.SendInputResponse(
                success=False,
                error=f"Session {session_id[:8]}... not connected"
            )

    async def SendResize(self, request, context):
        """Send resize command via unary RPC."""
        session_id = request.session_id
        cols = request.cols
        rows = request.rows

        logger.info(f"📐 SendResize RPC: session={session_id[:8]}..., {cols}x{rows}")

        success = await self.send_resize(session_id, cols, rows)

        if success:
            return pb2.SendResizeResponse(success=True)
        else:
            return pb2.SendResizeResponse(
                success=False,
                error=f"Session {session_id[:8]}... not connected"
            )

    async def SendSignal(self, request, context):
        """Send signal to terminal via unary RPC."""
        session_id = request.session_id
        signal = request.signal

        logger.info(f"⚡ SendSignal RPC: session={session_id[:8]}..., signal={signal}")

        success = await self.send_signal(session_id, signal)

        if success:
            return pb2.SendSignalResponse(success=True)
        else:
            return pb2.SendSignalResponse(
                success=False,
                error=f"Session {session_id[:8]}... not connected"
            )


class _ServicerCommandClient:
    """
    Adapter that allows command functions to work with servicer's session queues.

    Command functions expect a client with `_send_command(command)` method.
    This adapter bridges the gap between commands module and the servicer.
    """

    def __init__(self, session_id: str, queue: asyncio.Queue):
        self.session_id = session_id
        self._queue = queue

    async def _send_command(self, command) -> bool:
        """Put command in session's queue."""
        try:
            await self._queue.put(command)
            return True
        except Exception as e:
            logger.error(f"Failed to queue command: {e}")
            return False

    async def send_command_and_wait(self, command, timeout: float = 5.0):
        """
        Send command (fire-and-forget since servicer doesn't support sync).

        Note: Servicer-based client doesn't support waiting for ACK.
        Use StreamingCommandClient for sync operations.
        """
        success = await self._send_command(command)
        # Return mock ACK
        return type('CommandAck', (), {
            'command_id': command.command_id,
            'success': success,
            'message': 'Queued' if success else 'Failed'
        })()


# Singleton instance
_terminal_service: Optional[TerminalStreamingServiceServicer] = None


def get_terminal_service() -> TerminalStreamingServiceServicer:
    """Get or create singleton terminal service."""
    global _terminal_service
    if _terminal_service is None:
        _terminal_service = TerminalStreamingServiceServicer()
    return _terminal_service


def grpc_handlers(server) -> None:
    """
    Register terminal gRPC handlers.

    Called by django-cfg gRPC server via handlers_hook.
    """
    if not PROTO_AVAILABLE:
        logger.warning("Terminal proto not available, skipping gRPC registration")
        return

    service = get_terminal_service()
    pb2_grpc.add_TerminalStreamingServiceServicer_to_server(service, server)
    logger.info("Registered TerminalStreamingService")
