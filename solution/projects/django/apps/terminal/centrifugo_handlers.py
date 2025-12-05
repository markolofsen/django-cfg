"""
Terminal Centrifugo RPC handlers.

Handles terminal input from browser via Centrifugo RPC.
Uses @websocket_rpc decorator for type-safe RPC methods.
"""

import base64
import logging

from django.utils import timezone
from pydantic import BaseModel, Field

from django_cfg.apps.integrations.centrifugo.decorators import websocket_rpc

from apps.terminal.models import TerminalSession

logger = logging.getLogger(__name__)


# ========================
# Request/Response Models
# ========================

class TerminalInputParams(BaseModel):
    """Parameters for sending input to terminal."""
    session_id: str = Field(..., description="Terminal session UUID")
    data: str = Field(..., description="Input data (base64 encoded)")


class TerminalResizeParams(BaseModel):
    """Parameters for resizing terminal."""
    session_id: str = Field(..., description="Terminal session UUID")
    cols: int = Field(..., ge=1, le=500, description="Number of columns")
    rows: int = Field(..., ge=1, le=200, description="Number of rows")


class TerminalSignalParams(BaseModel):
    """Parameters for sending signal to terminal."""
    session_id: str = Field(..., description="Terminal session UUID")
    signal: int = Field(2, ge=1, le=31, description="Signal number (2=SIGINT, 9=SIGKILL, 15=SIGTERM)")


class TerminalCloseParams(BaseModel):
    """Parameters for closing terminal session."""
    session_id: str = Field(..., description="Terminal session UUID")
    reason: str = Field("", description="Reason for closing")


class CreateSessionParams(BaseModel):
    """Parameters for creating new terminal session."""
    name: str = Field("", description="Optional session name")
    shell: str = Field("/bin/zsh", description="Shell to use")
    working_directory: str = Field("~", description="Initial working directory")


class GetSessionParams(BaseModel):
    """Parameters for getting session info."""
    session_id: str = Field(..., description="Terminal session UUID")


class ListSessionsParams(BaseModel):
    """Parameters for listing sessions."""
    limit: int = Field(20, ge=1, le=100, description="Max sessions to return")


class SuccessResult(BaseModel):
    """Generic success result."""
    success: bool
    message: str = ""


class SessionResult(BaseModel):
    """Session info result."""
    session_id: str
    name: str
    status: str
    shell: str
    working_directory: str
    electron_hostname: str = ""
    commands_count: int = 0


class SessionListResult(BaseModel):
    """List of sessions result."""
    sessions: list[SessionResult]
    total: int


# ========================
# RPC Handlers
# ========================

@websocket_rpc("terminal.input")
async def terminal_input(conn, params: TerminalInputParams) -> SuccessResult:
    """
    Send input to terminal session.

    Forwards keyboard input from browser to Electron via gRPC.
    Data should be base64 encoded.
    """
    from .grpc.services.handlers import get_terminal_service

    try:
        # Decode base64 input
        data = base64.b64decode(params.data)

        # Forward to gRPC service
        service = get_terminal_service()
        success = await service.send_input(params.session_id, data)

        if success:
            return SuccessResult(success=True, message="Input sent")
        else:
            return SuccessResult(success=False, message="Session not connected")

    except Exception as e:
        logger.error(f"terminal.input error: {e}", exc_info=True)
        return SuccessResult(success=False, message=str(e))


@websocket_rpc("terminal.resize")
async def terminal_resize(conn, params: TerminalResizeParams) -> SuccessResult:
    """
    Resize terminal.

    Updates terminal dimensions in Electron PTY.
    """
    from .grpc.services.handlers import get_terminal_service

    try:
        service = get_terminal_service()
        success = await service.send_resize(
            params.session_id,
            params.cols,
            params.rows
        )

        if success:
            return SuccessResult(success=True, message=f"Resized to {params.cols}x{params.rows}")
        else:
            return SuccessResult(success=False, message="Session not connected")

    except Exception as e:
        logger.error(f"terminal.resize error: {e}", exc_info=True)
        return SuccessResult(success=False, message=str(e))


@websocket_rpc("terminal.signal")
async def terminal_signal(conn, params: TerminalSignalParams) -> SuccessResult:
    """
    Send signal to terminal process.

    Common signals:
    - 2 (SIGINT): Interrupt (Ctrl+C)
    - 9 (SIGKILL): Kill
    - 15 (SIGTERM): Terminate
    """
    from .grpc.services.handlers import get_terminal_service

    signal_names = {2: "SIGINT", 9: "SIGKILL", 15: "SIGTERM"}

    try:
        service = get_terminal_service()
        success = await service.send_signal(params.session_id, params.signal)

        signal_name = signal_names.get(params.signal, f"signal {params.signal}")

        if success:
            return SuccessResult(success=True, message=f"Sent {signal_name}")
        else:
            return SuccessResult(success=False, message="Session not connected")

    except Exception as e:
        logger.error(f"terminal.signal error: {e}", exc_info=True)
        return SuccessResult(success=False, message=str(e))


@websocket_rpc("terminal.close")
async def terminal_close(conn, params: TerminalCloseParams) -> SuccessResult:
    """
    Close terminal session.

    Sends close command to Electron and updates session status.
    """
    from .grpc.services.handlers import get_terminal_service

    try:
        service = get_terminal_service()
        await service.close_session(params.session_id, params.reason)

        # Update session status in DB
        await TerminalSession.objects.filter(
            id=params.session_id
        ).aupdate(
            status=TerminalSession.Status.DISCONNECTED,
            disconnected_at=timezone.now(),
        )

        return SuccessResult(success=True, message="Session closed")

    except Exception as e:
        logger.error(f"terminal.close error: {e}", exc_info=True)
        return SuccessResult(success=False, message=str(e))


@websocket_rpc("terminal.create_session")
async def create_session(conn, params: CreateSessionParams) -> SessionResult:
    """
    Create new terminal session.

    Creates session in database. Electron will connect via gRPC
    using the returned session_id.
    """
    session = await TerminalSession.objects.acreate(
        user_id=conn.user_id,
        name=params.name,
        shell=params.shell,
        working_directory=params.working_directory,
    )

    return SessionResult(
        session_id=str(session.id),
        name=session.name,
        status=session.status,
        shell=session.shell,
        working_directory=session.working_directory,
    )


@websocket_rpc("terminal.get_session")
async def get_session(conn, params: GetSessionParams) -> SessionResult:
    """
    Get terminal session info.
    """
    try:
        session = await TerminalSession.objects.aget(
            id=params.session_id,
            user_id=conn.user_id
        )

        return SessionResult(
            session_id=str(session.id),
            name=session.name,
            status=session.status,
            shell=session.shell,
            working_directory=session.working_directory,
            electron_hostname=session.electron_hostname or "",
            commands_count=session.commands_count,
        )

    except TerminalSession.DoesNotExist:
        raise ValueError("Session not found")


@websocket_rpc("terminal.list_sessions")
async def list_sessions(conn, params: ListSessionsParams) -> SessionListResult:
    """
    List user's terminal sessions.
    """
    limit = params.limit if params else 20
    sessions = await TerminalSession.objects.filter(
        user_id=conn.user_id
    ).order_by('-created_at')[:limit].alist()

    session_results = [
        SessionResult(
            session_id=str(s.id),
            name=s.name,
            status=s.status,
            shell=s.shell,
            working_directory=s.working_directory,
            electron_hostname=s.electron_hostname or "",
            commands_count=s.commands_count,
        )
        for s in sessions
    ]

    return SessionListResult(
        sessions=session_results,
        total=len(session_results)
    )
