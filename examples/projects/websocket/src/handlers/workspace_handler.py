"""
Workspace Event Handler.

Handles real-time workspace events:
- File changes (create, modify, delete, rename)
- File snapshots
- Workspace state updates
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

class FileChangeEvent(BaseModel):
    """File change event model."""
    workspace_id: str = Field(..., description="Workspace ID")
    file_path: str = Field(..., description="Relative file path")
    event_type: str = Field(..., description="create | modify | delete | rename")
    old_path: str | None = Field(None, description="Old path for rename events")
    content: str | None = Field(None, description="File content (for create/modify)")
    diff: str | None = Field(None, description="Git-style diff")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


class SnapshotEvent(BaseModel):
    """Snapshot event model."""
    workspace_id: str = Field(..., description="Workspace ID")
    snapshot_id: str = Field(..., description="Snapshot ID")
    name: str = Field(..., description="Snapshot name")
    description: str | None = Field(None, description="Snapshot description")
    created_at: str = Field(..., description="ISO 8601 timestamp")


# =============================================================================
# Workspace Handler
# =============================================================================

class WorkspaceHandler(BaseHandler):
    """
    Workspace event handler.

    RPC Methods:
        - workspace.file_changed: File change notifications
        - workspace.snapshot_created: Snapshot notifications
        - workspace.state_changed: Workspace state updates
    """

    async def initialize(self) -> None:
        """Initialize workspace handler."""
        self._log_info("Workspace handler initialized")

    def register(self, router: MessageRouter) -> None:
        """Register workspace methods with router."""
        if not self.enabled:
            self._log_info("Workspace handler disabled, skipping registration")
            return

        @router.register("workspace.file_changed")
        async def handle_file_changed(conn: ActiveConnection, params: dict):
            return await self.file_changed(conn, params)

        @router.register("workspace.snapshot_created")
        async def handle_snapshot_created(conn: ActiveConnection, params: dict):
            return await self.snapshot_created(conn, params)

        @router.register("workspace.state_changed")
        async def handle_state_changed(conn: ActiveConnection, params: dict):
            return await self.state_changed(conn, params)

        self._log_info("Registered workspace methods")

    async def file_changed(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Handle file change event."""
        # Validate params
        event = FileChangeEvent.model_validate(params)

        self._log_info(
            f"File changed: workspace={event.workspace_id} | "
            f"path={event.file_path} | type={event.event_type}"
        )

        return {
            "success": True,
            "message": f"File change recorded for workspace:{event.workspace_id}",
        }

    async def snapshot_created(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Handle snapshot created event."""
        # Validate params
        event = SnapshotEvent.model_validate(params)

        self._log_info(
            f"Snapshot created: workspace={event.workspace_id} | "
            f"snapshot={event.snapshot_id}"
        )

        return {
            "success": True,
            "message": f"Snapshot recorded for workspace:{event.workspace_id}",
        }

    async def state_changed(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """Handle workspace state change event."""
        workspace_id = params.get("workspace_id")
        state = params.get("state")

        if not workspace_id or not state:
            raise ValueError("workspace_id and state are required")

        self._log_info(
            f"State changed: workspace={workspace_id} | state={state}"
        )

        return {
            "success": True,
            "message": f"State change recorded for workspace:{workspace_id}",
        }
