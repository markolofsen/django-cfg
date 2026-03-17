"""
Global registry for RPC handlers and channels.

Stores metadata about registered handlers and channels for code generation.
"""

import hashlib
import json
import logging
import re
from typing import Dict, List, Any, Callable, Optional, Type, Union, get_args, get_origin
from pydantic import BaseModel
from dataclasses import dataclass, field

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
        no_wait: If True, method doesn't wait for response (fire-and-forget)
    """
    name: str
    handler: Callable
    param_type: Optional[Type[BaseModel]]
    return_type: Optional[Type[BaseModel]]
    docstring: Optional[str]
    no_wait: bool = False


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
        no_wait: bool = False,
    ) -> None:
        """
        Register RPC handler.

        Args:
            name: RPC method name (e.g., "tasks.get_stats")
            handler: Handler function
            param_type: Pydantic model for parameters
            return_type: Pydantic model for return value
            docstring: Handler documentation
            no_wait: If True, method doesn't wait for response (fire-and-forget)
        """
        if name in self._handlers:
            logger.warning(f"Handler '{name}' already registered, overwriting")

        self._handlers[name] = RegisteredHandler(
            name=name,
            handler=handler,
            param_type=param_type,
            return_type=return_type,
            docstring=docstring,
            no_wait=no_wait,
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

    def compute_api_version(self) -> str:
        """
        Compute a stable hash of the API contract.

        The hash is based on:
        - Method names and signatures
        - Model field names and types

        Returns a short hex hash (8 chars) that changes when the contract changes.
        """
        contract_data = {
            "methods": [],
            "models": [],
        }

        # Collect unique models
        models_seen = set()

        # Add method signatures
        for handler in sorted(self._handlers.values(), key=lambda h: h.name):
            contract_data["methods"].append({
                "name": handler.name,
                "param_type": handler.param_type.__name__ if handler.param_type else None,
                "return_type": handler.return_type.__name__ if handler.return_type else None,
                "no_wait": handler.no_wait,
            })

            # Collect models
            if handler.param_type:
                models_seen.add(handler.param_type)
            if handler.return_type:
                models_seen.add(handler.return_type)

        # Add model schemas
        for model in sorted(models_seen, key=lambda m: m.__name__):
            try:
                schema = model.model_json_schema()
                contract_data["models"].append({
                    "name": model.__name__,
                    "properties": sorted(schema.get("properties", {}).keys()),
                    "required": sorted(schema.get("required", [])),
                })
            except Exception as e:
                logger.warning(f"Could not get schema for {model.__name__}: {e}")

        # Compute hash
        contract_json = json.dumps(contract_data, sort_keys=True)
        full_hash = hashlib.sha256(contract_json.encode()).hexdigest()

        return full_hash[:8]


# Global registry instance
_global_registry = RPCRegistry()


def get_global_registry() -> RPCRegistry:
    """Get global RPC registry instance."""
    return _global_registry


# ========================
# Channel Registry
# ========================


@dataclass
class RegisteredChannel:
    """
    Metadata about registered Centrifugo channel for pub/sub.

    Attributes:
        name: Channel name (e.g., "ai_chat")
        pattern: Channel pattern with placeholders (e.g., "ai_chat:workspace:{workspace_id}")
        event_types: List of Pydantic event model classes
        docstring: Channel documentation
        params: List of parameter names extracted from pattern
    """

    name: str
    pattern: str
    event_types: List[Type[BaseModel]] = field(default_factory=list)
    docstring: Optional[str] = None
    params: List[str] = field(default_factory=list)

    @classmethod
    def from_pattern(
        cls,
        name: str,
        pattern: str,
        event_types: List[Type[BaseModel]],
        docstring: Optional[str] = None,
    ) -> "RegisteredChannel":
        """Create RegisteredChannel extracting params from pattern."""
        params = re.findall(r'\{(\w+)\}', pattern)
        return cls(
            name=name,
            pattern=pattern,
            event_types=event_types,
            docstring=docstring,
            params=params,
        )


def _extract_event_types_from_union(union_type: Any) -> List[Type[BaseModel]]:
    """
    Extract all Pydantic model types from a Union type.

    Args:
        union_type: A Union type like Union[EventA, EventB, EventC]

    Returns:
        List of Pydantic BaseModel subclasses
    """
    import inspect

    event_types = []

    # Check if it's a Union type
    origin = get_origin(union_type)
    if origin is Union:
        args = get_args(union_type)
        for arg in args:
            try:
                if inspect.isclass(arg) and issubclass(arg, BaseModel):
                    event_types.append(arg)
            except (TypeError, AttributeError):
                pass
    elif hasattr(union_type, '__mro__') and issubclass(union_type, BaseModel):
        event_types.append(union_type)

    return event_types


class ChannelRegistry:
    """
    Global registry for Centrifugo channels.

    Used by @centrifugo_channel decorator to register channels
    and by codegen to discover available channels for subscription generation.
    """

    def __init__(self):
        self._channels: Dict[str, RegisteredChannel] = {}

    def register(
        self,
        name: str,
        pattern: str,
        event_type: Any,  # Union[EventA, EventB, ...] or single EventType
        docstring: Optional[str] = None,
    ) -> None:
        """
        Register a Centrifugo channel.

        Args:
            name: Channel name (e.g., "ai_chat")
            pattern: Channel pattern with placeholders (e.g., "ai_chat:workspace:{workspace_id}")
            event_type: Union type of event models or single event model
            docstring: Channel documentation
        """
        if name in self._channels:
            logger.warning(f"Channel '{name}' already registered, overwriting")

        # Extract event types from Union
        event_types = _extract_event_types_from_union(event_type)

        if not event_types:
            logger.warning(
                f"⚠️  Channel '{name}' has no valid Pydantic event types. "
                f"Subscription code generation requires Pydantic models."
            )

        channel = RegisteredChannel.from_pattern(
            name=name,
            pattern=pattern,
            event_types=event_types,
            docstring=docstring,
        )

        self._channels[name] = channel
        logger.debug(f"Registered channel: {name} with {len(event_types)} event types")

    def get_channel(self, name: str) -> Optional[RegisteredChannel]:
        """Get channel by name."""
        return self._channels.get(name)

    def get_all_channels(self) -> List[RegisteredChannel]:
        """Get all registered channels."""
        return list(self._channels.values())

    def list_channels(self) -> List[str]:
        """List all registered channel names."""
        return list(self._channels.keys())

    def clear(self) -> None:
        """Clear all registered channels (for testing)."""
        self._channels.clear()


# Global channel registry instance
_global_channel_registry = ChannelRegistry()


def get_global_channel_registry() -> ChannelRegistry:
    """Get global channel registry instance."""
    return _global_channel_registry


__all__ = [
    "RegisteredHandler",
    "RPCRegistry",
    "get_global_registry",
    "RegisteredChannel",
    "ChannelRegistry",
    "get_global_channel_registry",
]
