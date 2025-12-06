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
    import grpc

    try:
        from .grpc.services.generated import terminal_streaming_service_pb2 as pb2
        from .grpc.services.generated import terminal_streaming_service_pb2_grpc as pb2_grpc
    except ImportError:
        logger.error("Proto files not generated")
        return SuccessResult(success=False, message="Proto files not generated")

    try:
        # Decode base64 input
        data = base64.b64decode(params.data)

        # Forward to gRPC server via client
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = pb2_grpc.TerminalStreamingServiceStub(channel)
            request = pb2.SendInputRequest(session_id=params.session_id, data=data)
            response = await stub.SendInput(request)

            if response.success:
                return SuccessResult(success=True, message="Input sent")
            else:
                return SuccessResult(success=False, message=response.error or "Session not connected")

    except grpc.aio.AioRpcError as e:
        logger.error(f"terminal.input gRPC error: {e.code()}: {e.details()}")
        return SuccessResult(success=False, message=f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"terminal.input error: {e}", exc_info=True)
        return SuccessResult(success=False, message=str(e))


@websocket_rpc("terminal.resize")
async def terminal_resize(conn, params: TerminalResizeParams) -> SuccessResult:
    """
    Resize terminal.

    Updates terminal dimensions in Electron PTY.
    """
    import grpc

    try:
        from .grpc.services.generated import terminal_streaming_service_pb2 as pb2
        from .grpc.services.generated import terminal_streaming_service_pb2_grpc as pb2_grpc
    except ImportError:
        return SuccessResult(success=False, message="Proto files not generated")

    try:
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = pb2_grpc.TerminalStreamingServiceStub(channel)
            request = pb2.SendResizeRequest(
                session_id=params.session_id,
                cols=params.cols,
                rows=params.rows
            )
            response = await stub.SendResize(request)

            if response.success:
                return SuccessResult(success=True, message=f"Resized to {params.cols}x{params.rows}")
            else:
                return SuccessResult(success=False, message=response.error or "Session not connected")

    except grpc.aio.AioRpcError as e:
        logger.error(f"terminal.resize gRPC error: {e.code()}: {e.details()}")
        return SuccessResult(success=False, message=f"gRPC error: {e.details()}")
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
    import grpc

    try:
        from .grpc.services.generated import terminal_streaming_service_pb2 as pb2
        from .grpc.services.generated import terminal_streaming_service_pb2_grpc as pb2_grpc
    except ImportError:
        return SuccessResult(success=False, message="Proto files not generated")

    signal_names = {2: "SIGINT", 9: "SIGKILL", 15: "SIGTERM"}

    try:
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = pb2_grpc.TerminalStreamingServiceStub(channel)
            request = pb2.SendSignalRequest(
                session_id=params.session_id,
                signal=params.signal
            )
            response = await stub.SendSignal(request)

            signal_name = signal_names.get(params.signal, f"signal {params.signal}")

            if response.success:
                return SuccessResult(success=True, message=f"Sent {signal_name}")
            else:
                return SuccessResult(success=False, message=response.error or "Session not connected")

    except grpc.aio.AioRpcError as e:
        logger.error(f"terminal.signal gRPC error: {e.code()}: {e.details()}")
        return SuccessResult(success=False, message=f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"terminal.signal error: {e}", exc_info=True)
        return SuccessResult(success=False, message=str(e))


@websocket_rpc("terminal.close")
async def terminal_close(conn, params: TerminalCloseParams) -> SuccessResult:
    """
    Close terminal session.

    Sends close command to Electron and updates session status.
    """
    import grpc

    try:
        from .grpc.services.generated import terminal_streaming_service_pb2 as pb2
        from .grpc.services.generated import terminal_streaming_service_pb2_grpc as pb2_grpc
    except ImportError:
        return SuccessResult(success=False, message="Proto files not generated")

    try:
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = pb2_grpc.TerminalStreamingServiceStub(channel)
            request = pb2.CloseSessionRequest(
                session_id=params.session_id,
                reason=params.reason
            )
            response = await stub.CloseSession(request)

            # Update session status in DB regardless of gRPC response
            await TerminalSession.objects.filter(
                id=params.session_id
            ).aupdate(
                status=TerminalSession.Status.DISCONNECTED,
                disconnected_at=timezone.now(),
            )

            if response.success:
                return SuccessResult(success=True, message="Session closed")
            else:
                return SuccessResult(success=False, message=response.error or "Failed to close")

    except grpc.aio.AioRpcError as e:
        logger.error(f"terminal.close gRPC error: {e.code()}: {e.details()}")
        return SuccessResult(success=False, message=f"gRPC error: {e.details()}")
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
