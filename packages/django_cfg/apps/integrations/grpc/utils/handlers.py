"""
gRPC handler factory utilities.

This module provides utilities for creating and registering gRPC servicers
with proper error handling and logging.

**Purpose**:
Simplify the boilerplate code needed to register gRPC services with servers.

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.utils.handlers import create_grpc_handler

# Your servicer class
class BotStreamingService(pb2_grpc.BotStreamingServiceServicer):
    pass

# Create handler tuple
handlers = create_grpc_handler(
    servicer_class=BotStreamingService,
    add_servicer_func=pb2_grpc.add_BotStreamingServiceServicer_to_server,
)

# Use with django-cfg
GRPC_HANDLERS = [handlers]
```

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

from typing import Callable, Tuple, Any, Optional, Type
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Handler Factory
# ============================================================================

def create_grpc_handler(
    servicer_class: Type,
    add_servicer_func: Callable[[Any, Any], None],
    servicer_kwargs: Optional[dict] = None,
) -> Tuple[Callable[[Any, Any], None], Type, dict]:
    """
    Create gRPC handler tuple for django-cfg GRPC_HANDLERS.

    This factory creates the standardized tuple format expected by django-cfg's
    gRPC server initialization:
    ```python
    (add_servicer_function, servicer_class, init_kwargs)
    ```

    Args:
        servicer_class: gRPC servicer class (e.g., MyStreamingService)
        add_servicer_func: Generated add_*_to_server function from pb2_grpc
        servicer_kwargs: Optional kwargs to pass to servicer constructor

    Returns:
        Tuple of (add_func, servicer_class, kwargs) for GRPC_HANDLERS

    Example:
    ```python
    from .generated import bot_streaming_service_pb2_grpc
    from .services import BotStreamingService

    handlers = create_grpc_handler(
        servicer_class=BotStreamingService,
        add_servicer_func=bot_streaming_service_pb2_grpc.add_BotStreamingServiceServicer_to_server,
        servicer_kwargs={'config': my_config},
    )

    # In settings.py
    GRPC_HANDLERS = [handlers]
    ```

    **django-cfg Integration**:
    The tuple is used by django-cfg like this:
    ```python
    for add_func, servicer_class, kwargs in GRPC_HANDLERS:
        servicer = servicer_class(**kwargs)
        add_func(servicer, server)
    ```
    """
    kwargs = servicer_kwargs or {}

    logger.debug(
        f"Created gRPC handler: {servicer_class.__name__} "
        f"with {len(kwargs)} init kwargs"
    )

    return (add_servicer_func, servicer_class, kwargs)


def create_multiple_grpc_handlers(
    handlers_config: list[dict],
) -> list[Tuple[Callable[[Any, Any], None], Type, dict]]:
    """
    Create multiple gRPC handlers from configuration list.

    Convenience function for creating multiple handlers at once.

    Args:
        handlers_config: List of handler configurations, each with keys:
            - servicer_class: Servicer class
            - add_servicer_func: Add function
            - servicer_kwargs: Optional init kwargs

    Returns:
        List of handler tuples for GRPC_HANDLERS

    Example:
    ```python
    handlers = create_multiple_grpc_handlers([
        {
            'servicer_class': BotStreamingService,
            'add_servicer_func': pb2_grpc.add_BotStreamingServiceServicer_to_server,
        },
        {
            'servicer_class': SignalStreamingService,
            'add_servicer_func': signal_pb2_grpc.add_SignalStreamingServiceServicer_to_server,
            'servicer_kwargs': {'timeout': 30},
        },
    ])

    # In settings.py
    GRPC_HANDLERS = handlers
    ```
    """
    handlers = []

    for config in handlers_config:
        handler = create_grpc_handler(
            servicer_class=config['servicer_class'],
            add_servicer_func=config['add_servicer_func'],
            servicer_kwargs=config.get('servicer_kwargs'),
        )
        handlers.append(handler)

    logger.info(f"Created {len(handlers)} gRPC handlers")

    return handlers


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_grpc_handler(
    handler: Tuple[Callable, Type, dict],
) -> bool:
    """
    Validate that handler tuple has correct structure.

    Args:
        handler: Handler tuple to validate

    Returns:
        True if valid, False otherwise

    Example:
    ```python
    handler = create_grpc_handler(MyService, add_func)

    if validate_grpc_handler(handler):
        GRPC_HANDLERS.append(handler)
    ```
    """
    if not isinstance(handler, tuple):
        logger.error(f"Handler must be tuple, got {type(handler)}")
        return False

    if len(handler) != 3:
        logger.error(f"Handler tuple must have 3 elements, got {len(handler)}")
        return False

    add_func, servicer_class, kwargs = handler

    if not callable(add_func):
        logger.error(f"First element (add_func) must be callable, got {type(add_func)}")
        return False

    if not isinstance(servicer_class, type):
        logger.error(f"Second element (servicer_class) must be class, got {type(servicer_class)}")
        return False

    if not isinstance(kwargs, dict):
        logger.error(f"Third element (kwargs) must be dict, got {type(kwargs)}")
        return False

    return True


def validate_grpc_handlers(
    handlers: list,
) -> Tuple[bool, list[str]]:
    """
    Validate list of handlers.

    Args:
        handlers: List of handler tuples

    Returns:
        Tuple of (all_valid: bool, errors: list[str])

    Example:
    ```python
    valid, errors = validate_grpc_handlers(GRPC_HANDLERS)

    if not valid:
        for error in errors:
            logger.error(error)
        raise ValueError("Invalid gRPC handlers")
    ```
    """
    errors = []

    if not isinstance(handlers, list):
        errors.append(f"GRPC_HANDLERS must be list, got {type(handlers)}")
        return False, errors

    for i, handler in enumerate(handlers):
        if not validate_grpc_handler(handler):
            errors.append(f"Handler #{i} is invalid")

    all_valid = len(errors) == 0
    return all_valid, errors


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'create_grpc_handler',
    'create_multiple_grpc_handlers',
    'validate_grpc_handler',
    'validate_grpc_handlers',
]
