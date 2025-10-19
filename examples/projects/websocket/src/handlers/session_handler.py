"""
AI Session Handler.

Handles real-time AI session events:
- Session messages (AI responses streaming)
- Task status updates
- Context updates
"""

from typing import Any, Dict
from pydantic import BaseModel, Field, ValidationError
from django_ipc.handlers import BaseHandler
from django_ipc.server.connection_manager import ActiveConnection
from django_ipc.server.message_router import MessageRouter
from loguru import logger


# =============================================================================
# Pydantic Models
# =============================================================================

class SessionMessageEvent(BaseModel):
    """AI session message event."""
    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(..., description="Message ID")
    role: str = Field(..., description="user | assistant | system")
    content: str = Field(..., description="Message content")
    is_streaming: bool = Field(default=False, description="Is streaming chunk")
    is_final: bool = Field(default=True, description="Is final message")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


class TaskStatusEvent(BaseModel):
    """AI task status event."""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="pending | running | completed | failed")
    progress: int | None = Field(None, description="Progress percentage (0-100)")
    result: str | None = Field(None, description="Task result")
    error: str | None = Field(None, description="Error message")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


# =============================================================================
# Session Handler
# =============================================================================

class SessionHandler(BaseHandler):
    """
    AI Session event handler.

    RPC Methods:
        - session.message: AI message streaming
        - session.task_status: Task status updates
        - session.context_updated: Context change notifications
    """

    async def initialize(self) -> None:
        """Initialize session handler."""
        self._log_info("Session handler initialized")

    def register(self, router: MessageRouter) -> None:
        """Register session methods with router."""
        if not self.enabled:
            self._log_info("Session handler disabled, skipping registration")
            return

        @router.register("session.message")
        async def handle_message(conn: ActiveConnection, params: dict):
            return await self.message(conn, params)

        @router.register("session.task_status")
        async def handle_task_status(conn: ActiveConnection, params: dict):
            return await self.task_status(conn, params)

        @router.register("session.context_updated")
        async def handle_context_updated(conn: ActiveConnection, params: dict):
            return await self.context_updated(conn, params)

        self._log_info("Registered session methods")

    async def message(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Handle AI session message (streaming)."""
        # Validate params
        event = SessionMessageEvent.model_validate(params)

        self._log_info(
            f"Message: session={event.session_id} | "
            f"role={event.role} | streaming={event.is_streaming}"
        )

        return {
            "success": True,
            "message": f"Message recorded for session:{event.session_id}",
        }

    async def task_status(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Handle AI task status update."""
        # Validate params
        event = TaskStatusEvent.model_validate(params)

        self._log_info(
            f"Task status: task={event.task_id} | status={event.status}"
        )

        return {
            "success": True,
            "message": f"Task status recorded for task:{event.task_id}",
        }

    async def context_updated(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Handle session context update."""
        session_id = params.get("session_id")
        context_data = params.get("context")

        if not session_id or not context_data:
            raise ValueError("session_id and context are required")

        self._log_info(f"Context updated: session={session_id}")

        return {
            "success": True,
            "message": f"Context update recorded for session:{session_id}",
        }
