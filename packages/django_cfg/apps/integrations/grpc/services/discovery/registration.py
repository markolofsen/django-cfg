"""
Service registration for gRPC.

Provides discover_and_register_services function.
"""

from typing import List, Tuple, Union

import grpc
import grpc.aio

from django_cfg.utils import get_logger

from .service_discovery import ServiceDiscovery
from .utils import extract_service_name

logger = get_logger("grpc.registration")

# Type alias for both sync and async gRPC servers
GRPCServer = Union[grpc.Server, grpc.aio.Server]


def discover_and_register_services(server: GRPCServer) -> Tuple[int, List[str]]:
    """
    Discover and register all gRPC services to a server.

    Args:
        server: gRPC server instance

    Returns:
        Tuple of (number of services registered, list of full service names for reflection)

    Example:
        ```python
        import grpc
        from concurrent import futures
        from django_cfg.apps.integrations.grpc.services.discovery import discover_and_register_services

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        count, service_names = discover_and_register_services(server)
        print(f"Registered {count} services: {service_names}")

        server.add_insecure_port('[::]:50051')
        server.start()
        ```
    """
    logger.info("=" * 60)
    logger.info("discover_and_register_services: STARTING")
    logger.info("=" * 60)

    discovery = ServiceDiscovery()
    count = 0
    service_names: List[str] = []

    # Process handlers hooks first
    count, service_names = _process_handlers_hooks(discovery, server, count, service_names)

    # Discover and register services
    count, service_names = _register_discovered_services(discovery, server, count, service_names)

    logger.info(f"Registered {count} gRPC service(s): {service_names}")
    return count, service_names


def _process_handlers_hooks(
    discovery: ServiceDiscovery,
    server: GRPCServer,
    count: int,
    service_names: List[str],
) -> Tuple[int, List[str]]:
    """Process all handlers hooks."""
    handlers_hooks = discovery.get_handlers_hooks()
    logger.info(f"discover_and_register_services: got {len(handlers_hooks)} handlers_hooks")

    for hook in handlers_hooks:
        logger.info(f"discover_and_register_services: calling hook {hook}")
        try:
            result = hook(server)
            logger.info(f"Successfully called handlers hook: {hook.__name__}")

            # Extract service names from the result
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, tuple) and len(item) >= 1:
                        service_class = item[0]
                        service_name = extract_service_name(service_class)
                        service_names.append(service_name)
                        logger.debug(f"Extracted service name: {service_name}")

            count += 1

        except Exception as e:
            logger.error(f"Error calling handlers hook {hook.__name__}: {e}", exc_info=True)

    return count, service_names


def _register_discovered_services(
    discovery: ServiceDiscovery,
    server: GRPCServer,
    count: int,
    service_names: List[str],
) -> Tuple[int, List[str]]:
    """Register discovered services."""
    services = discovery.discover_services()

    for service_class, add_to_server_func in services:
        try:
            servicer = service_class()
            add_to_server_func(servicer, server)

            service_name = extract_service_name(service_class)
            service_names.append(service_name)

            logger.debug(f"Registered service: {service_class.__name__}")
            count += 1

        except Exception as e:
            logger.error(
                f"Failed to register service {service_class.__name__}: {e}",
                exc_info=True,
            )

    return count, service_names


__all__ = ["discover_and_register_services"]
