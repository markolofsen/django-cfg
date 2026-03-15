"""
MessageRouter for Centrifugo RPC handlers.

Compatible with legacy WebSocket solution's MessageRouter interface for code generation.
"""

import logging
from typing import Dict, Callable, Any

logger = logging.getLogger(__name__)


class MessageRouter:
    """
    Message router for Centrifugo RPC handlers.

    Provides legacy WebSocket solution compatible interface for handler registration
    and discovery by codegen system.
    """

    def __init__(self):
        """Initialize message router."""
        self._handlers: Dict[str, Callable] = {}

    def register(self, method_name: str):
        """
        Decorator to register RPC handler.

        Args:
            method_name: RPC method name (e.g., "tasks.get_stats")

        Returns:
            Decorator function

        Example:
            >>> router = MessageRouter()
            >>>
            >>> @router.register("tasks.get_stats")
            >>> async def handle_get_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
            ...     return TaskStatsResult(total=100, completed=50)
        """
        def decorator(handler_func: Callable) -> Callable:
            if method_name in self._handlers:
                logger.warning(f"Handler '{method_name}' already registered, overwriting")

            self._handlers[method_name] = handler_func
            logger.debug(f"Registered handler: {method_name}")

            return handler_func

        return decorator

    def get_handler(self, method_name: str) -> Callable:
        """
        Get handler by method name.

        Args:
            method_name: RPC method name

        Returns:
            Handler function

        Raises:
            KeyError: If handler not found
        """
        return self._handlers[method_name]

    def has_handler(self, method_name: str) -> bool:
        """
        Check if handler exists.

        Args:
            method_name: RPC method name

        Returns:
            True if handler registered
        """
        return method_name in self._handlers

    def list_methods(self) -> list[str]:
        """
        List all registered method names.

        Returns:
            List of method names
        """
        return list(self._handlers.keys())

    async def handle_message(self, method_name: str, params: Any, conn: Any = None) -> Any:
        """
        Handle RPC message.

        Args:
            method_name: RPC method name
            params: Method parameters
            conn: Connection object (optional)

        Returns:
            Handler result

        Raises:
            KeyError: If handler not found
        """
        handler = self.get_handler(method_name)

        # Call handler with or without connection
        if conn is not None:
            return await handler(conn, params)
        else:
            return await handler(params)


# Global router instance
_global_router = MessageRouter()


def get_global_router() -> MessageRouter:
    """Get global MessageRouter instance."""
    return _global_router


__all__ = [
    "MessageRouter",
    "get_global_router",
]
