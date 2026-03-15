"""
Decorators for Centrifugo RPC handlers and channels.
"""

import logging
import inspect
from typing import Any, Callable, Optional, Type, get_type_hints
from pydantic import BaseModel

from .router import get_global_router
from .registry import get_global_registry, get_global_channel_registry

logger = logging.getLogger(__name__)


def websocket_rpc(method_name: str, *, no_wait: bool = False):
    """
    Decorator to register WebSocket RPC handler.

    Registers handler with both MessageRouter (for runtime)
    and RPCRegistry (for code generation).

    Args:
        method_name: RPC method name (e.g., "tasks.get_stats")
        no_wait: If True, client won't wait for response (fire-and-forget)

    Returns:
        Decorator function

    Example:
        >>> from pydantic import BaseModel
        >>>
        >>> class TaskStatsParams(BaseModel):
        ...     date_from: str
        ...     date_to: str
        >>>
        >>> class TaskStatsResult(BaseModel):
        ...     total: int
        ...     completed: int
        >>>
        >>> @websocket_rpc("tasks.get_stats")
        >>> async def get_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
        ...     # Business logic here
        ...     return TaskStatsResult(total=100, completed=50)
        >>>
        >>> # Fire-and-forget example:
        >>> @websocket_rpc("terminal.input", no_wait=True)
        >>> async def terminal_input(conn, params: TerminalInputParams) -> SuccessResult:
        ...     # Process input without client waiting
        ...     return SuccessResult(success=True)

    Notes:
        - Handler must be async function
        - Handler signature: async def handler(conn, params: ParamsModel) -> ResultModel
        - ParamsModel and ResultModel must be Pydantic BaseModel subclasses
        - Type hints are required for code generation
        - Use no_wait=True for methods where client shouldn't wait for response
    """
    def decorator(handler_func: Callable) -> Callable:
        # Validate handler is async
        if not inspect.iscoroutinefunction(handler_func):
            raise TypeError(f"Handler '{method_name}' must be async function")

        # Store no_wait attribute on function for discovery
        handler_func._no_wait = no_wait  # type: ignore

        # Extract type hints
        try:
            hints = get_type_hints(handler_func)
        except Exception as e:
            logger.warning(f"Could not extract type hints for '{method_name}': {e}")
            hints = {}

        # Extract parameter type (second parameter after conn)
        param_type: Optional[Type[BaseModel]] = None
        signature = inspect.signature(handler_func)
        params_list = list(signature.parameters.values())

        if len(params_list) >= 2:
            params_param = params_list[1]
            param_type_hint = hints.get(params_param.name)

            if param_type_hint and _is_pydantic_model(param_type_hint):
                param_type = param_type_hint
            elif param_type_hint:
                logger.warning(
                    f"⚠️  Handler '{method_name}' uses '{param_type_hint}' for params. "
                    f"Pydantic models recommended for type-safe client generation."
                )

        # Extract return type
        return_type: Optional[Type[BaseModel]] = None
        return_type_hint = hints.get("return")

        if return_type_hint and _is_pydantic_model(return_type_hint):
            return_type = return_type_hint
        elif return_type_hint:
            logger.warning(
                f"⚠️  Handler '{method_name}' returns '{return_type_hint}'. "
                f"Pydantic models recommended for type-safe client generation."
            )

        # Get docstring
        docstring = inspect.getdoc(handler_func)

        # Register with MessageRouter (for runtime)
        router = get_global_router()
        router.register(method_name)(handler_func)

        # Register with RPCRegistry (for codegen)
        registry = get_global_registry()
        registry.register(
            name=method_name,
            handler=handler_func,
            param_type=param_type,
            return_type=return_type,
            docstring=docstring,
            no_wait=no_wait,
        )

        logger.info(f"✅ Registered WebSocket RPC: {method_name}")

        return handler_func

    return decorator


def _is_pydantic_model(type_hint) -> bool:
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


def centrifugo_channel(
    name: str,
    pattern: str,
    event_type: Any,
    docstring: Optional[str] = None,
) -> None:
    """
    Register a Centrifugo channel for pub/sub.

    This function registers a channel with the global channel registry.
    The channel info is used by codegen to generate typed subscription methods.

    Args:
        name: Channel name (e.g., "ai_chat")
        pattern: Channel pattern with placeholders (e.g., "ai_chat:workspace:{workspace_id}")
        event_type: Union type of Pydantic event models (e.g., Union[MessageStart, MessageChunk])
        docstring: Channel documentation

    Example:
        >>> from typing import Union
        >>> from pydantic import BaseModel
        >>>
        >>> class MessageStart(BaseModel):
        ...     type: str = "message_start"
        ...     message_id: str
        >>>
        >>> class MessageChunk(BaseModel):
        ...     type: str = "message_chunk"
        ...     chunk: str
        >>>
        >>> AIChatEvent = Union[MessageStart, MessageChunk]
        >>>
        >>> centrifugo_channel(
        ...     name="ai_chat",
        ...     pattern="ai_chat:workspace:{workspace_id}",
        ...     event_type=AIChatEvent,
        ...     docstring="AI chat streaming events",
        ... )

    Notes:
        - Event models must have a 'type' field with a Literal default for discriminated unions
        - Pattern placeholders (e.g., {workspace_id}) become parameters in generated code
        - Call this at module load time (e.g., in apps.py ready() or channels.py)
    """
    registry = get_global_channel_registry()
    registry.register(
        name=name,
        pattern=pattern,
        event_type=event_type,
        docstring=docstring,
    )

    logger.info(f"✅ Registered Centrifugo channel: {name} ({pattern})")


__all__ = [
    "websocket_rpc",
    "centrifugo_channel",
]
