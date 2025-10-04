"""
Notification Handler for WebSocket RPC.

Handles sending notifications to connected users.

File size: ~400 lines
"""

from typing import Dict, Any
from pydantic import ValidationError

from ..models import (
    NotificationRequest,
    NotificationResponse,
    BatchNotificationRequest,
    BatchNotificationResponse,
    UserNotConnectedError,
    RPCErrorCode,
)
from ..server.connection_manager import ActiveConnection
from ..server.message_router import MessageRouter
from .base import BaseHandler


class NotificationHandler(BaseHandler):
    """
    Handler for user notifications.

    Provides RPC methods for sending notifications to connected users.

    Supported methods:
        - send_notification: Send notification to single user
        - send_batch_notifications: Send notifications to multiple users

    Example:
        >>> handler = NotificationHandler(connection_manager, enabled=True)
        >>> handler.register(router)
        >>>
        >>> # From Django:
        >>> result = rpc_client.call(
        ...     method="send_notification",
        ...     params=NotificationRequest(
        ...         user_id="123",
        ...         type="info",
        ...         title="New message",
        ...         message="You have a new message",
        ...     ),
        ...     result_model=NotificationResponse,
        ... )
    """

    async def initialize(self) -> None:
        """Initialize notification handler."""
        self._log_info("Notification handler initialized")

    def register(self, router: MessageRouter) -> None:
        """
        Register notification methods with router.

        Args:
            router: MessageRouter instance
        """
        if not self.enabled:
            self._log_info("Notification handler disabled, skipping registration")
            return

        @router.register("send_notification")
        async def handle_send_notification(conn: ActiveConnection, params: dict):
            return await self.send_notification(conn, params)

        @router.register("send_batch_notifications")
        async def handle_batch_notifications(conn: ActiveConnection, params: dict):
            return await self.send_batch_notifications(conn, params)

        self._log_info("Registered notification methods")

    async def send_notification(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """
        Send notification to a user.

        Args:
            conn: Connection info (caller)
            params: Notification parameters

        Returns:
            NotificationResponse dict

        Raises:
            ValidationError: If params are invalid
            UserNotConnectedError: If user not connected
        """
        # Validate params with Pydantic
        try:
            request = NotificationRequest.model_validate(params)
        except ValidationError:
            raise

        # Check if user is online
        is_online = await self.connection_manager.is_user_online(request.user_id)

        if not is_online:
            # User not connected - return error response
            self._log_debug(f"User {request.user_id} not connected")
            response = NotificationResponse(
                user_id=request.user_id,
                delivered=False,
                connections=0,
                error=f"User {request.user_id} is not connected",
            )
            return response.model_dump()

        # Prepare notification message
        notification_message = {
            "type": "notification",
            "data": {
                "notification_type": request.type,  # Already a string
                "title": request.title,
                "message": request.message,
                "data": request.data,
                "priority": request.priority.value,  # Enum -> string
            },
        }

        # Send to all user connections
        sent_count = await self._send_to_user(request.user_id, notification_message)

        self._log_debug(
            f"Sent notification to user {request.user_id} "
            f"({sent_count} connections)"
        )

        # Return response
        response = NotificationResponse(
            user_id=request.user_id,
            delivered=True,
            connections=sent_count,
        )

        return response.model_dump()

    async def send_batch_notifications(
        self,
        conn: ActiveConnection,
        params: dict,
    ) -> dict:
        """
        Send notifications to multiple users.

        Args:
            conn: Connection info (caller)
            params: Batch notification parameters

        Returns:
            BatchNotificationResponse dict

        Raises:
            ValidationError: If params are invalid
        """
        # Validate params
        try:
            request = BatchNotificationRequest.model_validate(params)
        except ValidationError:
            raise

        results = []
        total_delivered = 0
        total_failed = 0

        # Process each notification
        for notif_req in request.notifications:
            # Check if user is online
            is_online = await self.connection_manager.is_user_online(notif_req.user_id)

            if not is_online:
                # Skip offline users
                results.append(
                    NotificationResponse(
                        user_id=notif_req.user_id,
                        delivered=False,
                        connections=0,
                        error="User not connected",
                    ).model_dump()
                )
                total_failed += 1
                continue

            # Prepare notification message
            notification_message = {
                "type": "notification",
                "data": {
                    "notification_type": notif_req.type,  # Already a string
                    "title": notif_req.title,
                    "message": notif_req.message,
                    "data": notif_req.data,
                    "priority": notif_req.priority.value,  # Enum -> string
                },
            }

            # Send to user
            try:
                sent_count = await self._send_to_user(notif_req.user_id, notification_message)

                results.append(
                    NotificationResponse(
                        user_id=notif_req.user_id,
                        delivered=True,
                        connections=sent_count,
                    ).model_dump()
                )
                total_delivered += 1

            except Exception as e:
                self._log_warning(f"Failed to send notification to {notif_req.user_id}: {e}")
                results.append(
                    NotificationResponse(
                        user_id=notif_req.user_id,
                        delivered=False,
                        connections=0,
                        error=str(e),
                    ).model_dump()
                )
                total_failed += 1

        self._log_debug(
            f"Batch notifications: {total_delivered} delivered, {total_failed} failed"
        )

        # Return batch response
        response = BatchNotificationResponse(
            total=len(request.notifications),
            delivered=total_delivered,
            failed=total_failed,
            results=results,
        )

        return response.model_dump()


__all__ = [
    "NotificationHandler",
]
