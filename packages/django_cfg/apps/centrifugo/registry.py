"""
Global registry for RPC handlers.

Stores metadata about registered handlers for code generation.
"""

import logging
from typing import Dict, List, Any, Callable, Optional, Type
from pydantic import BaseModel
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RegisteredHandler:
    """
    Metadata about registered RPC handler.

    Attributes:
        name: RPC method name (e.g., "tasks.get_stats")
        handler: Handler function
        param_type: Pydantic model for parameters
        return_type: Pydantic model for return value
        docstring: Handler documentation
    """
    name: str
    handler: Callable
    param_type: Optional[Type[BaseModel]]
    return_type: Optional[Type[BaseModel]]
    docstring: Optional[str]


class RPCRegistry:
    """
    Global registry for RPC handlers.

    Used by @websocket_rpc decorator to register handlers
    and by codegen to discover available methods.
    """

    def __init__(self):
        self._handlers: Dict[str, RegisteredHandler] = {}

    def register(
        self,
        name: str,
        handler: Callable,
        param_type: Optional[Type[BaseModel]] = None,
        return_type: Optional[Type[BaseModel]] = None,
        docstring: Optional[str] = None,
    ) -> None:
        """
        Register RPC handler.

        Args:
            name: RPC method name (e.g., "tasks.get_stats")
            handler: Handler function
            param_type: Pydantic model for parameters
            return_type: Pydantic model for return value
            docstring: Handler documentation
        """
        if name in self._handlers:
            logger.warning(f"Handler '{name}' already registered, overwriting")

        self._handlers[name] = RegisteredHandler(
            name=name,
            handler=handler,
            param_type=param_type,
            return_type=return_type,
            docstring=docstring,
        )

        logger.debug(f"Registered RPC handler: {name}")

    def get_handler(self, name: str) -> Optional[RegisteredHandler]:
        """Get handler by name."""
        return self._handlers.get(name)

    def get_all_handlers(self) -> List[RegisteredHandler]:
        """Get all registered handlers."""
        return list(self._handlers.values())

    def list_methods(self) -> List[str]:
        """List all registered method names."""
        return list(self._handlers.keys())

    def clear(self) -> None:
        """Clear all registered handlers (for testing)."""
        self._handlers.clear()


# Global registry instance
_global_registry = RPCRegistry()


def get_global_registry() -> RPCRegistry:
    """Get global RPC registry instance."""
    return _global_registry


__all__ = [
    "RegisteredHandler",
    "RPCRegistry",
    "get_global_registry",
]
