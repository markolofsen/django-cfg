"""
Base Handler for WebSocket RPC.

Provides abstract base class for all WebSocket handlers.

File size: ~300 lines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger

from ..server.connection_manager import ConnectionManager, ActiveConnection
from ..server.message_router import MessageRouter


class BaseHandler(ABC):
    """
    Abstract base class for WebSocket handlers.

    All built-in and custom handlers should inherit from this class.
    Provides access to ConnectionManager and MessageRouter.

    Example:
        >>> class MyHandler(BaseHandler):
        ...     def register(self, router: MessageRouter) -> None:
        ...         @router.register("my_method")
        ...         async def handle_my_method(conn: ActiveConnection, params: dict):
        ...             return await self.my_method(conn, params)
        ...
        ...     async def my_method(
        ...         self,
        ...         conn: ActiveConnection,
        ...         params: dict,
        ...     ) -> dict:
        ...         # Implementation
        ...         return {"status": "ok"}
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        enabled: bool = True,
    ):
        """
        Initialize base handler.

        Args:
            connection_manager: ConnectionManager instance
            enabled: Whether handler is enabled
        """
        self.connection_manager = connection_manager
        self.enabled = enabled
        self._router: Optional[MessageRouter] = None

    @abstractmethod
    def register(self, router: MessageRouter) -> None:
        """
        Register handler methods with router.

        This method must be implemented by subclasses to register
        their methods/types with the message router.

        Args:
            router: MessageRouter instance

        Example:
            >>> def register(self, router: MessageRouter) -> None:
            ...     @router.register("echo")
            ...     async def handle_echo(conn: ActiveConnection, params: dict):
            ...         return await self.echo(conn, params)
        """
        pass

    async def initialize(self) -> None:
        """
        Initialize handler.

        Override this method to perform async initialization.
        Called when server starts.
        """
        pass

    async def shutdown(self) -> None:
        """
        Shutdown handler.

        Override this method to perform cleanup.
        Called when server shuts down.
        """
        pass

    def _log_debug(self, message: str) -> None:
        """
        Log debug message with handler name.

        Args:
            message: Log message
        """
        logger.debug(f"[{self.__class__.__name__}] {message}")

    def _log_info(self, message: str) -> None:
        """
        Log info message with handler name.

        Args:
            message: Log message
        """
        logger.info(f"[{self.__class__.__name__}] {message}")

    def _log_warning(self, message: str) -> None:
        """
        Log warning message with handler name.

        Args:
            message: Log message
        """
        logger.warning(f"[{self.__class__.__name__}] {message}")

    def _log_error(self, message: str) -> None:
        """
        Log error message with handler name.

        Args:
            message: Log message
        """
        logger.error(f"[{self.__class__.__name__}] {message}")

    async def _send_to_connection(
        self,
        conn: ActiveConnection,
        message: dict,
    ) -> bool:
        """
        Send message to specific connection.

        Args:
            conn: Connection info
            message: Message dict

        Returns:
            True if sent successfully
        """
        try:
            await conn.websocket.send(str(message))
            conn.update_activity()
            return True
        except Exception as e:
            self._log_warning(f"Failed to send to connection {conn.connection_id}: {e}")
            return False

    async def _send_to_user(
        self,
        user_id: str,
        message: dict,
    ) -> int:
        """
        Send message to all user connections.

        Args:
            user_id: User ID
            message: Message dict

        Returns:
            Number of connections sent to
        """
        return await self.connection_manager.send_to_user(user_id, message)

    async def _send_to_room(
        self,
        room: str,
        message: dict,
    ) -> int:
        """
        Send message to all room connections.

        Args:
            room: Room name
            message: Message dict

        Returns:
            Number of connections sent to
        """
        return await self.connection_manager.send_to_room(room, message)

    async def _broadcast(
        self,
        message: dict,
    ) -> int:
        """
        Broadcast message to all connections.

        Args:
            message: Message dict

        Returns:
            Number of connections sent to
        """
        return await self.connection_manager.broadcast(message)

    def _validate_params(
        self,
        params: dict,
        required_fields: list,
    ) -> None:
        """
        Validate required parameters exist.

        Args:
            params: Parameters dict
            required_fields: List of required field names

        Raises:
            ValueError: If required field is missing
        """
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")


__all__ = [
    "BaseHandler",
]
