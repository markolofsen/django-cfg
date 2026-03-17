"""
Method and channel discovery for code generation.

Scans registered RPC handlers and channels, extracts type information.
Supports IntEnum discovery for enum code generation.
"""

import inspect
import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Type, List, Optional, Any, get_type_hints, Dict, Union, get_args, get_origin
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# For type checking in warnings
try:
    from typing import _GenericAlias  # For Dict[str, Any] checks
except ImportError:
    _GenericAlias = type(None)


@dataclass
class ChannelInfo:
    """
    Information about a Centrifugo channel for subscriptions.

    Attributes:
        name: Channel name pattern (e.g., "ai_chat")
        pattern: Channel pattern with placeholders (e.g., "ai_chat:workspace:{workspace_id}")
        event_types: List of Pydantic event model classes
        docstring: Channel documentation
        params: List of parameter names from pattern (e.g., ["workspace_id"])
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
    ) -> "ChannelInfo":
        """Create ChannelInfo extracting params from pattern."""
        import re
        params = re.findall(r'\{(\w+)\}', pattern)
        return cls(
            name=name,
            pattern=pattern,
            event_types=event_types,
            docstring=docstring,
            params=params,
        )


@dataclass
class RPCMethodInfo:
    """
    Information about discovered RPC method.

    Attributes:
        name: Method name (e.g., "send_notification")
        handler_func: Handler function reference
        param_type: Pydantic model for parameters (if available)
        return_type: Pydantic model for return value (if available)
        docstring: Method documentation
        no_wait: If True, method doesn't wait for response (fire-and-forget)
    """

    name: str
    handler_func: Any
    param_type: Optional[Type[BaseModel]]
    return_type: Optional[Type[BaseModel]]
    docstring: Optional[str]
    no_wait: bool = False


def discover_rpc_methods_from_router(router: Any) -> List[RPCMethodInfo]:
    """
    Discover RPC methods from MessageRouter instance.

    Args:
        router: MessageRouter instance with registered handlers

    Returns:
        List of discovered method information

    Example:
        >>> # Legacy router import removed
        >>> router = MessageRouter(connection_manager)
        >>>
        >>> @router.register("echo")
        >>> async def handle_echo(conn, params: EchoParams) -> EchoResult:
        ...     return EchoResult(message=params.message)
        >>>
        >>> methods = discover_rpc_methods_from_router(router)
        >>> methods[0].name
        'echo'
        >>> methods[0].param_type
        <class 'EchoParams'>
    """
    methods = []

    # Get registered handlers from router
    handlers = getattr(router, "_handlers", {})

    if not handlers:
        logger.warning("No handlers found in router._handlers")
        return methods

    logger.info(f"Discovering {len(handlers)} RPC methods from router")

    for method_name, handler_func in handlers.items():
        try:
            method_info = _extract_method_info(method_name, handler_func)
            methods.append(method_info)
            logger.debug(f"Discovered method: {method_name}")
        except Exception as e:
            logger.error(f"Failed to extract info for {method_name}: {e}")

    return methods


def _extract_method_info(method_name: str, handler_func: Any) -> RPCMethodInfo:
    """
    Extract type information from handler function.

    Args:
        method_name: Name of the method
        handler_func: Handler function

    Returns:
        RPCMethodInfo with extracted type information
    """
    # Get function signature
    signature = inspect.signature(handler_func)

    # Get type hints
    try:
        hints = get_type_hints(handler_func)
    except Exception as e:
        logger.debug(f"Could not get type hints for {method_name}: {e}")
        hints = {}

    # Extract parameter type
    # Handler signature: async def handler(conn: ActiveConnection, params: Dict[str, Any])
    # We're looking for the 'params' parameter type
    param_type = None
    params_list = list(signature.parameters.values())

    if len(params_list) >= 2:
        # Second parameter should be params
        params_param = params_list[1]
        param_type_hint = hints.get(params_param.name)

        # Check if it's a Pydantic model
        if param_type_hint and _is_pydantic_model(param_type_hint):
            param_type = param_type_hint
        elif param_type_hint and not _is_generic_dict(param_type_hint):
            # Warn if using non-Pydantic type (but not dict/Dict[str, Any])
            logger.warning(
                f"⚠️  Method '{method_name}' uses '{param_type_hint}' for params instead of Pydantic model. "
                f"Type-safe client generation requires Pydantic models."
            )

    # Extract return type
    return_type = None
    return_type_hint = hints.get("return")

    if return_type_hint and _is_pydantic_model(return_type_hint):
        return_type = return_type_hint

    # Get docstring
    docstring = inspect.getdoc(handler_func)

    # Check for no_wait attribute (fire-and-forget mode)
    no_wait = getattr(handler_func, '_no_wait', False)

    return RPCMethodInfo(
        name=method_name,
        handler_func=handler_func,
        param_type=param_type,
        return_type=return_type,
        docstring=docstring,
        no_wait=no_wait,
    )


def _is_pydantic_model(type_hint: Any) -> bool:
    """
    Check if type hint is a Pydantic model.

    Args:
        type_hint: Type hint to check

    Returns:
        True if it's a Pydantic BaseModel subclass
    """
    try:
        return (
            inspect.isclass(type_hint)
            and issubclass(type_hint, BaseModel)
        )
    except (TypeError, AttributeError):
        return False


def _is_generic_dict(type_hint: Any) -> bool:
    """
    Check if type hint is dict or Dict[str, Any].

    Args:
        type_hint: Type hint to check

    Returns:
        True if it's dict or Dict type
    """
    if type_hint is dict:
        return True

    # Check for Dict[str, Any] or similar generic dict types
    type_str = str(type_hint)
    if 'dict' in type_str.lower() or 'Dict' in type_str:
        return True

    return False


def extract_all_models(methods: List[RPCMethodInfo]) -> List[Type[BaseModel]]:
    """
    Extract all unique Pydantic models from discovered methods.

    Args:
        methods: List of discovered method information

    Returns:
        List of unique Pydantic models (both params and returns)
    """
    models = set()

    for method in methods:
        if method.param_type:
            models.add(method.param_type)
        if method.return_type:
            models.add(method.return_type)

    return sorted(list(models), key=lambda m: m.__name__)


def get_method_summary(methods: List[RPCMethodInfo]) -> str:
    """
    Get human-readable summary of discovered methods.

    Args:
        methods: List of discovered method information

    Returns:
        Formatted summary string
    """
    lines = [f"Discovered {len(methods)} RPC methods:\n"]

    for method in methods:
        param_name = method.param_type.__name__ if method.param_type else "Dict[str, Any]"
        return_name = method.return_type.__name__ if method.return_type else "Dict[str, Any]"

        lines.append(f"  • {method.name}({param_name}) -> {return_name}")

        if method.docstring:
            # First line of docstring
            doc_first_line = method.docstring.split("\n")[0].strip()
            lines.append(f"    └─ {doc_first_line}")

    return "\n".join(lines)


# Backward compatibility: support importing from old path
discover_rpc_methods = discover_rpc_methods_from_router


def extract_event_types_from_union(union_type: Any) -> List[Type[BaseModel]]:
    """
    Extract all Pydantic model types from a Union type.

    Args:
        union_type: A Union type like Union[EventA, EventB, EventC]

    Returns:
        List of Pydantic BaseModel subclasses
    """
    event_types = []

    # Check if it's a Union type
    origin = get_origin(union_type)
    if origin is Union:
        args = get_args(union_type)
        for arg in args:
            if _is_pydantic_model(arg):
                event_types.append(arg)
    elif _is_pydantic_model(union_type):
        event_types.append(union_type)

    return event_types


def extract_all_channel_models(channels: List[ChannelInfo]) -> List[Type[BaseModel]]:
    """
    Extract all unique Pydantic models from channel event types.

    Args:
        channels: List of channel information

    Returns:
        List of unique Pydantic models for events
    """
    models = set()

    for channel in channels:
        for event_type in channel.event_types:
            models.add(event_type)
            # Also extract nested models from event fields
            _extract_nested_models(event_type, models)

    return sorted(list(models), key=lambda m: m.__name__)


def _extract_nested_models(model: Type[BaseModel], models: set) -> None:
    """Recursively extract nested Pydantic models from a model."""
    try:
        hints = get_type_hints(model)
        for field_name, field_type in hints.items():
            # Handle Optional, List, etc.
            origin = get_origin(field_type)
            if origin is Union:
                for arg in get_args(field_type):
                    if _is_pydantic_model(arg) and arg not in models:
                        models.add(arg)
                        _extract_nested_models(arg, models)
            elif origin is list:
                args = get_args(field_type)
                if args and _is_pydantic_model(args[0]) and args[0] not in models:
                    models.add(args[0])
                    _extract_nested_models(args[0], models)
            elif _is_pydantic_model(field_type) and field_type not in models:
                models.add(field_type)
                _extract_nested_models(field_type, models)
    except Exception:
        pass  # Ignore type hint extraction errors


def _is_int_enum(type_hint: Any) -> bool:
    """Check if type hint is an IntEnum subclass."""
    try:
        return inspect.isclass(type_hint) and issubclass(type_hint, IntEnum)
    except (TypeError, AttributeError):
        return False


def extract_enums_from_module(module: Any) -> List[Type[IntEnum]]:
    """
    Extract all IntEnum classes from a module.

    Args:
        module: Python module to scan

    Returns:
        List of IntEnum subclasses defined in the module
    """
    enums = []

    for name in dir(module):
        obj = getattr(module, name)
        if _is_int_enum(obj) and obj.__module__ == module.__name__:
            enums.append(obj)

    return sorted(enums, key=lambda e: e.__name__)


def extract_enums_from_models(models: List[Type[BaseModel]]) -> List[Type[IntEnum]]:
    """
    Extract all unique IntEnum types used in Pydantic models.

    Scans model field annotations for IntEnum types, including nested models.

    Args:
        models: List of Pydantic model classes

    Returns:
        List of unique IntEnum subclasses
    """
    enums = set()
    visited_models = set()

    def _extract_from_model(model: Type[BaseModel]) -> None:
        if model in visited_models:
            return
        visited_models.add(model)

        try:
            hints = get_type_hints(model)
            for field_name, field_type in hints.items():
                _collect_enums_from_type(field_type, enums)
                # Also recursively check nested Pydantic models
                _collect_nested_models_for_enums(field_type, _extract_from_model)
        except Exception as e:
            logger.debug(f"Could not get type hints for {model.__name__}: {e}")

    for model in models:
        _extract_from_model(model)

    return sorted(list(enums), key=lambda e: e.__name__)


def _collect_nested_models_for_enums(type_hint: Any, callback) -> None:
    """Recursively find nested Pydantic models and call callback for enum extraction."""
    # Direct Pydantic model
    if _is_pydantic_model(type_hint):
        callback(type_hint)
        return

    # Handle Optional, List, Union
    origin = get_origin(type_hint)
    if origin is Union:
        for arg in get_args(type_hint):
            _collect_nested_models_for_enums(arg, callback)
    elif origin is list:
        args = get_args(type_hint)
        if args:
            _collect_nested_models_for_enums(args[0], callback)


def _collect_enums_from_type(type_hint: Any, enums: set) -> None:
    """Recursively collect IntEnum types from a type hint."""
    # Direct IntEnum
    if _is_int_enum(type_hint):
        enums.add(type_hint)
        return

    # Handle Optional, List, Union
    origin = get_origin(type_hint)
    if origin is Union:
        for arg in get_args(type_hint):
            _collect_enums_from_type(arg, enums)
    elif origin is list:
        args = get_args(type_hint)
        if args:
            _collect_enums_from_type(args[0], enums)


__all__ = [
    "RPCMethodInfo",
    "ChannelInfo",
    "discover_rpc_methods_from_router",
    "discover_rpc_methods",
    "extract_all_models",
    "extract_all_channel_models",
    "extract_event_types_from_union",
    "extract_enums_from_module",
    "extract_enums_from_models",
    "get_method_summary",
]
