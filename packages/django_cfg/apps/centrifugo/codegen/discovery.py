"""
Method discovery for code generation.

Scans registered RPC handlers and extracts type information.
"""

import inspect
import logging
from dataclasses import dataclass
from typing import Type, List, Optional, Any, get_type_hints, Dict
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# For type checking in warnings
try:
    from typing import _GenericAlias  # For Dict[str, Any] checks
except ImportError:
    _GenericAlias = type(None)


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
    """

    name: str
    handler_func: Any
    param_type: Optional[Type[BaseModel]]
    return_type: Optional[Type[BaseModel]]
    docstring: Optional[str]


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

    return RPCMethodInfo(
        name=method_name,
        handler_func=handler_func,
        param_type=param_type,
        return_type=return_type,
        docstring=docstring,
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


__all__ = [
    "RPCMethodInfo",
    "discover_rpc_methods_from_router",
    "discover_rpc_methods",
    "extract_all_models",
    "get_method_summary",
]
