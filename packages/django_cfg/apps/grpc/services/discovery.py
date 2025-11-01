"""
Service Discovery for gRPC.

Automatically discovers and registers gRPC services from Django apps.
"""

import importlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)


class ServiceDiscovery:
    """
    Discovers gRPC services from Django applications.

    Features:
    - Auto-discovers services from enabled apps
    - Supports custom service registration
    - Configurable discovery paths
    - Lazy loading support
    - Integration with django-grpc-framework

    Example:
        ```python
        from django_cfg.apps.grpc.services.discovery import ServiceDiscovery

        discovery = ServiceDiscovery()
        services = discovery.discover_services()

        for service_class, add_to_server_func in services:
            add_to_server_func(service_class.as_servicer(), server)
        ```
    """

    def __init__(self):
        """Initialize service discovery."""
        self.grpc_config = getattr(settings, "GRPC_FRAMEWORK", {})
        self.auto_register = self.grpc_config.get("AUTO_REGISTER_APPS", True)
        self.enabled_apps = self.grpc_config.get("ENABLED_APPS", [])
        self.custom_services = self.grpc_config.get("CUSTOM_SERVICES", {})

        # Common module names where services might be defined
        self.service_modules = [
            "grpc_services",
            "grpc_handlers",
            "services.grpc",
            "handlers.grpc",
            "api.grpc",
        ]

    def discover_services(self) -> List[Tuple[Any, Any]]:
        """
        Discover all gRPC services.

        Returns:
            List of (service_class, add_to_server_func) tuples

        Example:
            >>> discovery = ServiceDiscovery()
            >>> services = discovery.discover_services()
            >>> len(services)
            5
        """
        discovered_services = []

        # Discover from enabled apps
        if self.auto_register:
            for app_label in self.enabled_apps:
                services = self._discover_app_services(app_label)
                discovered_services.extend(services)

        # Add custom services
        for service_path in self.custom_services.values():
            service = self._load_custom_service(service_path)
            if service:
                discovered_services.append(service)

        logger.info(f"Discovered {len(discovered_services)} gRPC service(s)")
        return discovered_services

    def _discover_app_services(self, app_label: str) -> List[Tuple[Any, Any]]:
        """
        Discover services from a Django app.

        Args:
            app_label: Django app label (e.g., 'accounts', 'support')

        Returns:
            List of discovered services
        """
        services = []

        # Get app config
        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            logger.warning(f"App '{app_label}' not found in INSTALLED_APPS")
            return services

        # Try to import service modules
        for module_name in self.service_modules:
            full_module_path = f"{app_config.name}.{module_name}"

            try:
                module = importlib.import_module(full_module_path)
                logger.debug(f"Found gRPC module: {full_module_path}")

                # Look for services in module
                app_services = self._extract_services_from_module(module, full_module_path)
                services.extend(app_services)

            except ImportError:
                # Module doesn't exist, that's okay
                logger.debug(f"No gRPC module at {full_module_path}")
                continue
            except Exception as e:
                logger.error(f"Error importing {full_module_path}: {e}", exc_info=True)
                continue

        if services:
            logger.info(f"Discovered {len(services)} service(s) from app '{app_label}'")

        return services

    def _extract_services_from_module(
        self, module: Any, module_path: str
    ) -> List[Tuple[Any, Any]]:
        """
        Extract gRPC services from a module.

        Args:
            module: Python module object
            module_path: Full module path string

        Returns:
            List of (service_class, add_to_server_func) tuples
        """
        services = []

        # Look for grpc_handlers() function (django-grpc-framework convention)
        if hasattr(module, "grpc_handlers"):
            handlers_func = getattr(module, "grpc_handlers")
            if callable(handlers_func):
                try:
                    # Call the handlers function to get list of services
                    handlers = handlers_func(None)  # server argument not needed for discovery
                    logger.info(f"Found grpc_handlers() in {module_path}")

                    # handlers should be a list of tuples
                    if isinstance(handlers, list):
                        services.extend(handlers)
                    else:
                        logger.warning(
                            f"grpc_handlers() in {module_path} did not return a list"
                        )

                except Exception as e:
                    logger.error(
                        f"Error calling grpc_handlers() in {module_path}: {e}",
                        exc_info=True,
                    )

        # Look for individual service classes
        for attr_name in dir(module):
            # Skip private attributes
            if attr_name.startswith("_"):
                continue

            attr = getattr(module, attr_name)

            # Check if it's a gRPC service class
            if self._is_grpc_service(attr):
                logger.debug(f"Found gRPC service class: {module_path}.{attr_name}")

                # Try to get add_to_server function
                add_to_server_func = self._get_add_to_server_func(attr, module_path)

                if add_to_server_func:
                    services.append((attr, add_to_server_func))

        return services

    def _is_grpc_service(self, obj: Any) -> bool:
        """
        Check if object is a gRPC service class.

        Args:
            obj: Object to check

        Returns:
            True if object is a gRPC service class
        """
        # Check if it's a class
        if not isinstance(obj, type):
            return False

        # Check for django-grpc-framework service
        try:
            from django_grpc_framework import generics

            # Check if it inherits from any generics service
            if issubclass(obj, (
                generics.Service,
                generics.ModelService,
                generics.ReadOnlyModelService,
            )):
                return True

        except ImportError:
            logger.debug("django-grpc-framework not installed, skipping service check")

        # Check for grpc servicer (has add_to_server method)
        if hasattr(obj, "add_to_server") and callable(getattr(obj, "add_to_server")):
            return True

        return False

    def _get_add_to_server_func(self, service_class: Any, module_path: str) -> Optional[Any]:
        """
        Get add_to_server function for a service class.

        Args:
            service_class: Service class
            module_path: Module path for logging

        Returns:
            add_to_server function or None
        """
        # For django-grpc-framework services
        if hasattr(service_class, "add_to_server"):
            return getattr(service_class, "add_to_server")

        # Try to find matching _pb2_grpc module
        # Convention: myservice.grpc_services.MyService -> myservice_pb2_grpc.add_MyServiceServicer_to_server
        try:
            # Get the module name without the service module part
            base_module = module_path.rsplit(".", 1)[0]
            pb2_grpc_module_name = f"{base_module}_pb2_grpc"

            pb2_grpc_module = importlib.import_module(pb2_grpc_module_name)

            # Look for add_<ServiceName>_to_server function
            func_name = f"add_{service_class.__name__}_to_server"

            if hasattr(pb2_grpc_module, func_name):
                return getattr(pb2_grpc_module, func_name)

        except ImportError:
            logger.debug(f"No _pb2_grpc module found for {module_path}")
        except Exception as e:
            logger.debug(f"Error finding add_to_server for {service_class.__name__}: {e}")

        return None

    def _load_custom_service(self, service_path: str) -> Optional[Tuple[Any, Any]]:
        """
        Load a custom service from dotted path.

        Args:
            service_path: Dotted path to service class (e.g., 'myapp.services.MyService')

        Returns:
            (service_class, add_to_server_func) tuple or None
        """
        try:
            # Split module path and class name
            module_path, class_name = service_path.rsplit(".", 1)

            # Import module
            module = importlib.import_module(module_path)

            # Get service class
            service_class = getattr(module, class_name)

            # Get add_to_server function
            add_to_server_func = self._get_add_to_server_func(service_class, module_path)

            if not add_to_server_func:
                logger.warning(
                    f"Custom service {service_path} has no add_to_server function"
                )
                return None

            logger.info(f"Loaded custom service: {service_path}")
            return (service_class, add_to_server_func)

        except ImportError as e:
            logger.error(f"Failed to import custom service {service_path}: {e}")
            return None
        except AttributeError as e:
            logger.error(f"Service class not found in {service_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading custom service {service_path}: {e}", exc_info=True)
            return None

    def get_handlers_hook(self) -> Optional[Any]:
        """
        Get the handlers hook function from ROOT_HANDLERS_HOOK setting.

        Returns:
            Handlers hook function or None

        Example:
            >>> discovery = ServiceDiscovery()
            >>> handlers_hook = discovery.get_handlers_hook()
            >>> if handlers_hook:
            ...     services = handlers_hook(server)
        """
        handlers_hook_path = self.grpc_config.get("ROOT_HANDLERS_HOOK")

        if not handlers_hook_path:
            logger.debug("No ROOT_HANDLERS_HOOK configured")
            return None

        try:
            # Import the module containing the hook
            module_path, func_name = handlers_hook_path.rsplit(".", 1)
            module = importlib.import_module(module_path)

            # Get the hook function
            handlers_hook = getattr(module, func_name)

            if not callable(handlers_hook):
                logger.warning(f"ROOT_HANDLERS_HOOK {handlers_hook_path} is not callable")
                return None

            logger.info(f"Loaded handlers hook: {handlers_hook_path}")
            return handlers_hook

        except ImportError as e:
            logger.error(f"Failed to import handlers hook {handlers_hook_path}: {e}")
            return None
        except AttributeError as e:
            logger.error(f"Handlers hook function not found in {handlers_hook_path}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Error loading handlers hook {handlers_hook_path}: {e}",
                exc_info=True,
            )
            return None


def discover_and_register_services(server: Any) -> int:
    """
    Discover and register all gRPC services to a server.

    Args:
        server: gRPC server instance

    Returns:
        Number of services registered

    Example:
        ```python
        import grpc
        from concurrent import futures
        from django_cfg.apps.grpc.services.discovery import discover_and_register_services

        # Create server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Auto-discover and register services
        count = discover_and_register_services(server)
        print(f"Registered {count} services")

        # Start server
        server.add_insecure_port('[::]:50051')
        server.start()
        ```
    """
    discovery = ServiceDiscovery()
    count = 0

    # Try handlers hook first
    handlers_hook = discovery.get_handlers_hook()
    if handlers_hook:
        try:
            handlers_hook(server)
            logger.info("Successfully called handlers hook")
            count += 1  # We don't know exact count, but at least 1
        except Exception as e:
            logger.error(f"Error calling handlers hook: {e}", exc_info=True)

    # Discover and register services
    services = discovery.discover_services()

    for service_class, add_to_server_func in services:
        try:
            # Instantiate service
            servicer = service_class()

            # Register with server
            add_to_server_func(servicer, server)

            logger.debug(f"Registered service: {service_class.__name__}")
            count += 1

        except Exception as e:
            logger.error(
                f"Failed to register service {service_class.__name__}: {e}",
                exc_info=True,
            )

    logger.info(f"Registered {count} gRPC service(s)")
    return count


__all__ = ["ServiceDiscovery", "discover_and_register_services"]
