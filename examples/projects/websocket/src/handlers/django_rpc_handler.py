"""
Django RPC Handler for WebSocket Server.

Handles RPC requests FROM Django via Redis Streams.
This allows Django to call WebSocket methods (send notifications, etc.)
"""

from django_ipc.bridge import RPCBridge
from django_ipc.server.connection_manager import ConnectionManager
from loguru import logger


class DjangoRPCHandler:
    """
    Handles RPC requests from Django.

    Django sends requests via get_rpc_client() → Redis Stream → This handler

    Registered Methods:
        - notification.send: Send notification to specific user
        - notification.broadcast: Broadcast to all connected users
    """

    def __init__(
        self,
        redis_url: str,
        connection_manager: ConnectionManager,
    ):
        """
        Initialize Django RPC handler.

        Args:
            redis_url: Redis connection URL
            connection_manager: ConnectionManager for sending to users
        """
        self.connection_manager = connection_manager

        # Create RPCBridge for Django requests
        self.bridge = RPCBridge(
            redis_url=redis_url,
            request_stream="stream:requests",  # Django uses this stream
            consumer_group="django_rpc_group",
            consumer_name="websocket_1",
            response_key_prefix="list:response:",
            log_calls=True,
        )

        # Register RPC methods
        self._register_methods()

    def _register_methods(self):
        """Register RPC methods that Django can call."""

        @self.bridge.rpc_method("notification.send")
        async def send_notification(params: dict):
            """
            Send notification to specific user.

            Called from Django:
                rpc.call_dict(
                    method="notification.send",
                    params={"user_id": "123", "title": "Hi", "message": "Test"}
                )
            """
            user_id = params.get("user_id")
            title = params.get("title")
            message = params.get("message")
            notification_type = params.get("type", "info")

            logger.info(
                f"[Django RPC] notification.send: user={user_id} | "
                f"type={notification_type} | title={title}"
            )

            # Send to all user connections
            message_payload = {
                "type": "notification",
                "data": {
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                }
            }

            sent_count = await self.connection_manager.send_to_user(
                user_id=user_id,
                message=message_payload,
            )

            return {
                "success": True,
                "sent_to_connections": sent_count,
                "user_id": user_id,
            }

        @self.bridge.rpc_method("notification.broadcast")
        async def broadcast_notification(params: dict):
            """
            Broadcast notification to all connected users.

            Called from Django:
                rpc.call_dict(
                    method="notification.broadcast",
                    params={"title": "System", "message": "Maintenance in 5 min"}
                )
            """
            title = params.get("title")
            message = params.get("message")
            notification_type = params.get("type", "info")

            logger.info(
                f"[Django RPC] notification.broadcast: "
                f"type={notification_type} | title={title}"
            )

            # Broadcast to everyone
            message_payload = {
                "type": "notification",
                "data": {
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                }
            }

            sent_count = await self.connection_manager.broadcast(message_payload)

            return {
                "success": True,
                "sent_to_connections": sent_count,
            }

        logger.info("[Django RPC Handler] Registered methods: notification.send, notification.broadcast")

    async def start(self):
        """Start the RPC bridge (begins consuming from Redis)."""
        await self.bridge.start()
        logger.success("[Django RPC Handler] Started, listening for Django requests")

    async def stop(self):
        """Stop the RPC bridge."""
        await self.bridge.stop()
        logger.info("[Django RPC Handler] Stopped")
