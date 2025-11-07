"""
Global Service Registry for Streaming Services

Provides a global registry to store and retrieve BidirectionalStreamingService instances.
This enables same-process command sending from anywhere in the application.

Usage:
    # In your gRPC service initialization (handlers/__init__.py)
    from django_cfg.apps.integrations.grpc.commands.registry import register_streaming_service

    def grpc_handlers(server):
        servicer = YourStreamingService()
        register_streaming_service("your_service", servicer._streaming_service)
        # ... rest of setup

    # In your command client
    from django_cfg.apps.integrations.grpc.commands.registry import get_streaming_service

    service = get_streaming_service("your_service")
    client = CommandClient(client_id="123", streaming_service=service)

Documentation: See @commands/README.md § Global Service Registry
"""

import logging
from threading import RLock
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Global registry of streaming services
# Key: service name (e.g., "bots", "signals")
# Value: BidirectionalStreamingService instance
_streaming_services: Dict[str, Any] = {}

# Thread-safe lock for registry access
_registry_lock = RLock()


def register_streaming_service(name: str, service: Any) -> None:
    """
    Register a streaming service in the global registry.

    This should be called when the gRPC service is initialized,
    typically in the grpc_handlers() function.

    Args:
        name: Service name (e.g., "bots", "signals", "notifications")
        service: BidirectionalStreamingService instance

    Example:
        from your_app.grpc.server import YourStreamingService

        def grpc_handlers(server):
            servicer = YourStreamingService()
            register_streaming_service("your_service", servicer._streaming_service)
            # ... rest of setup
    """
    with _registry_lock:
        if name in _streaming_services:
            logger.warning(
                f"Streaming service '{name}' already registered, overwriting"
            )

        _streaming_services[name] = service
        logger.info(f"Registered streaming service: {name}")


def get_streaming_service(name: str) -> Optional[Any]:
    """
    Get a streaming service from the global registry.

    Args:
        name: Service name

    Returns:
        BidirectionalStreamingService instance or None if not found

    Example:
        service = get_streaming_service("bots")
        if service:
            client = CommandClient(client_id="123", streaming_service=service)
        else:
            # Service not registered, will use cross-process mode
            client = CommandClient(client_id="123", grpc_port=50051)
    """
    with _registry_lock:
        service = _streaming_services.get(name)

        if service is None:
            logger.debug(
                f"Streaming service '{name}' not found in registry. "
                f"Available: {list(_streaming_services.keys())}"
            )

        return service


def unregister_streaming_service(name: str) -> bool:
    """
    Unregister a streaming service from the global registry.

    Args:
        name: Service name

    Returns:
        True if service was unregistered, False if not found
    """
    with _registry_lock:
        if name in _streaming_services:
            del _streaming_services[name]
            logger.info(f"Unregistered streaming service: {name}")
            return True
        return False


def list_streaming_services() -> List[str]:
    """
    List all registered streaming service names.

    Returns:
        List of service names

    Example:
        >>> list_streaming_services()
        ['bots', 'signals', 'notifications']
    """
    with _registry_lock:
        return list(_streaming_services.keys())


def is_registered(name: str) -> bool:
    """
    Check if a streaming service is registered.

    Args:
        name: Service name

    Returns:
        True if registered, False otherwise
    """
    with _registry_lock:
        return name in _streaming_services


def clear_registry() -> None:
    """
    Clear all registered services.

    Warning: This should only be used in tests or during shutdown.
    """
    with _registry_lock:
        count = len(_streaming_services)
        _streaming_services.clear()
        logger.info(f"Cleared {count} streaming services from registry")


# Convenience alias for backward compatibility
set_streaming_service = register_streaming_service


__all__ = [
    'register_streaming_service',
    'get_streaming_service',
    'unregister_streaming_service',
    'list_streaming_services',
    'is_registered',
    'clear_registry',
    'set_streaming_service',  # alias
]
