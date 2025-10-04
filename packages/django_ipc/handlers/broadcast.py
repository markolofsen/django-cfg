"""
Broadcast Handler for WebSocket RPC.

Handles room-based broadcasting and room management.

File size: ~450 lines
"""

from typing import Dict, Any
from pydantic import ValidationError

from ..models import (
    BroadcastRequest,
    BroadcastResponse,
    RoomJoinRequest,
    RoomLeaveRequest,
    BroadcastTarget,
)
from ..server.connection_manager import ActiveConnection
from ..server.message_router import MessageRouter
from .base import BaseHandler


class BroadcastHandler(BaseHandler):
    """
    Handler for broadcasts and room management.

    Provides RPC methods for:
        - Broadcasting messages to rooms/users/all
        - Joining/leaving rooms
        - Room management

    Supported methods:
        - broadcast: Send message to target (room/user/all)
        - join_room: Join a room
        - leave_room: Leave a room

    Example:
        >>> handler = BroadcastHandler(connection_manager, enabled=True)
        >>> handler.register(router)
        >>>
        >>> # From Django:
        >>> result = rpc_client.call(
        ...     method="broadcast",
        ...     params=BroadcastRequest(
        ...         target=BroadcastTarget.ROOM,
        ...         room="game_123",
        ...         message={"event": "player_joined", "player": "Alice"},
        ...     ),
        ...     result_model=BroadcastResponse,
        ... )
    """

    async def initialize(self) -> None:
        """Initialize broadcast handler."""
        self._log_info("Broadcast handler initialized")

    def register(self, router: MessageRouter) -> None:
        """
        Register broadcast methods with router.

        Args:
            router: MessageRouter instance
        """
        if not self.enabled:
            self._log_info("Broadcast handler disabled, skipping registration")
            return

        @router.register("broadcast")
        async def handle_broadcast(conn: ActiveConnection, params: dict):
            return await self.broadcast(conn, params)

        @router.register("join_room")
        async def handle_join_room(conn: ActiveConnection, params: dict):
            return await self.join_room(conn, params)

        @router.register("leave_room")
        async def handle_leave_room(conn: ActiveConnection, params: dict):
            return await self.leave_room(conn, params)

        self._log_info("Registered broadcast methods")

    async def broadcast(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """
        Broadcast message to target.

        Args:
            conn: Connection info (caller)
            params: Broadcast parameters

        Returns:
            BroadcastResponse dict

        Raises:
            ValidationError: If params are invalid
        """
        # Validate params
        try:
            request = BroadcastRequest.model_validate(params)
        except ValidationError:
            raise

        # Prepare broadcast message
        broadcast_message = {
            "type": "broadcast",
            "data": request.message,
        }

        sent_count = 0

        # Send based on target
        if request.target == BroadcastTarget.ALL:
            # Broadcast to all connections
            sent_count = await self._broadcast(broadcast_message)
            self._log_debug(f"Broadcast to ALL: {sent_count} connections")

        elif request.target == BroadcastTarget.ROOM:
            # Broadcast to room
            if not request.room:
                raise ValueError("room is required for ROOM target")

            sent_count = await self._send_to_room(request.room, broadcast_message)
            self._log_debug(f"Broadcast to room '{request.room}': {sent_count} connections")

        elif request.target == BroadcastTarget.USER:
            # Broadcast to specific user
            if not request.user_id:
                raise ValueError("user_id is required for USER target")

            sent_count = await self._send_to_user(request.user_id, broadcast_message)
            self._log_debug(f"Broadcast to user '{request.user_id}': {sent_count} connections")

        elif request.target == BroadcastTarget.USERS:
            # Broadcast to multiple users
            if not request.user_ids:
                raise ValueError("user_ids is required for USERS target")

            for user_id in request.user_ids:
                count = await self._send_to_user(user_id, broadcast_message)
                sent_count += count

            self._log_debug(
                f"Broadcast to {len(request.user_ids)} users: {sent_count} connections"
            )

        # Return response
        response = BroadcastResponse(
            target=request.target,
            recipients=sent_count,
            room=request.room,
            user_id=request.user_id,
        )

        return response.model_dump()

    async def join_room(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """
        Join a room.

        Args:
            conn: Connection info (caller)
            params: Room join parameters

        Returns:
            Success response dict

        Raises:
            ValidationError: If params are invalid
        """
        # Validate params
        try:
            request = RoomJoinRequest.model_validate(params)
        except ValidationError:
            raise

        # Join room
        success = await self.connection_manager.join_room(
            conn.connection_id,
            request.room,
        )

        if not success:
            raise ValueError(f"Failed to join room: {request.room}")

        self._log_debug(
            f"Connection {conn.connection_id} joined room '{request.room}'"
        )

        # Send join notification to room if requested
        if request.notify_room:
            join_message = {
                "type": "room_event",
                "event": "user_joined",
                "room": request.room,
                "user_id": conn.user_id,
            }
            await self._send_to_room(request.room, join_message)

        return {
            "room": request.room,
            "joined": True,
        }

    async def leave_room(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """
        Leave a room.

        Args:
            conn: Connection info (caller)
            params: Room leave parameters

        Returns:
            Success response dict

        Raises:
            ValidationError: If params are invalid
        """
        # Validate params
        try:
            request = RoomLeaveRequest.model_validate(params)
        except ValidationError:
            raise

        # Leave room
        success = await self.connection_manager.leave_room(
            conn.connection_id,
            request.room,
        )

        if not success:
            raise ValueError(f"Failed to leave room: {request.room}")

        self._log_debug(
            f"Connection {conn.connection_id} left room '{request.room}'"
        )

        # Send leave notification to room if requested
        if request.notify_room:
            leave_message = {
                "type": "room_event",
                "event": "user_left",
                "room": request.room,
                "user_id": conn.user_id,
            }
            await self._send_to_room(request.room, leave_message)

        return {
            "room": request.room,
            "left": True,
        }


__all__ = [
    "BroadcastHandler",
]
