"""
Unrealon Notification Handler.

Handles system notifications for users.
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

class NotificationEvent(BaseModel):
    """System notification event."""
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    type: str = Field(default="info", description="info | success | warning | error")
    action_url: str | None = Field(None, description="Action URL")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


# =============================================================================
# Notification Handler
# =============================================================================

class NotificationHandler(BaseHandler):
    """
    Unrealon notification handler.

    RPC Methods:
        - notification.send: Send notification to user
        - notification.broadcast: Broadcast to all users
    """

    async def initialize(self) -> None:
        """Initialize notification handler."""
        self._log_info("Unrealon notification handler initialized")

    def register(self, router: MessageRouter) -> None:
        """Register notification methods with router."""
        if not self.enabled:
            self._log_info("Unrealon notification handler disabled, skipping registration")
            return

        @router.register("notification.send")
        async def handle_send(conn: ActiveConnection, params: dict):
            return await self.send(conn, params)

        @router.register("notification.broadcast")
        async def handle_broadcast(conn: ActiveConnection, params: dict):
            return await self.broadcast(conn, params)

        self._log_info("Registered Unrealon notification methods")

    async def send(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Send notification to specific user."""
        # Validate params
        event = NotificationEvent.model_validate(params)

        self._log_info(
            f"Notification queued: user={event.user_id} | "
            f"type={event.type} | title={event.title}"
        )

        # Just return success - broadcasting is done elsewhere
        return {
            "success": True,
            "message": f"Notification queued for user:{event.user_id}",
            "data": event.model_dump(),
        }

    async def broadcast(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Broadcast notification to all users."""
        title = params.get("title")
        message = params.get("message")
        notification_type = params.get("type", "info")

        if not title or not message:
            raise ValueError("title and message are required")

        self._log_info(
            f"Broadcast queued: type={notification_type} | title={title}"
        )

        # Just return success - broadcasting is done elsewhere
        return {
            "success": True,
            "message": "Notification queued for broadcast",
            "data": {
                "title": title,
                "message": message,
                "type": notification_type,
                "timestamp": params.get("timestamp"),
            }
        }
