"""
Service Discovery for gRPC.

Automatically discovers and registers gRPC services from Django apps.
"""

import importlib
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps

from django_cfg.modules.django_logging import get_logger

from ..management.config_helper import get_enabled_apps, get_grpc_config

logger = get_logger("grpc.discovery")

# Optional django-grpc-framework support
try:
    from django_grpc_framework import generics
    HAS_DJANGO_GRPC_FRAMEWORK = True
except ImportError:
    HAS_DJANGO_GRPC_FRAMEWORK = False
    generics = None
    logger.debug("django-grpc-framework not installed, skipping DRF-style service discovery")


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
        from django_cfg.apps.integrations.grpc.services.discovery import ServiceDiscovery

        discovery = ServiceDiscovery()
        services = discovery.discover_services()

        for service_class, add_to_server_func in services:
            add_to_server_func(service_class.as_servicer(), server)
        ```
    """

    def __init__(self):
        """Initialize service discovery."""
        # Get config from django-cfg using Pydantic2 pattern
        self.config = get_grpc_config()

        logger.warning(f"🔍 ServiceDiscovery.__init__: config = {self.config}")
        if self.config:
            logger.warning(f"🔍 handlers_hook = {self.config.handlers_hook}")

        if self.config:
            self.auto_register = self.config.auto_register_apps
            self.enabled_apps = self.config.enabled_apps if self.config.auto_register_apps else []
            self.custom_services = self.config.custom_services
        else:
            # Fallback if config not available
            self.auto_register = False
            self.enabled_apps = []
            self.custom_services = {}
            logger.warning("gRPC config not found, service discovery disabled")

        # Common module names where services might be defined
        # Dynamically check which modules exist instead of hardcoding
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
            >>> services = discover_services()
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
            logger.warning(
                f"[gRPC Discovery] App '{app_label}' not found in INSTALLED_APPS. "
                f"Either add it to INSTALLED_APPS or remove from grpc.enabled_apps in config"
            )
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

        # Check for django-grpc-framework service (optional, if installed)
        if HAS_DJANGO_GRPC_FRAMEWORK and generics:
            try:
                # Check if it inherits from any generics service
                if issubclass(obj, (
                    generics.Service,
                    generics.ModelService,
                    generics.ReadOnlyModelService,
                )):
                    return True
            except (TypeError, AttributeError):
                # Not a valid subclass check
                pass

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

    def get_registered_services(self) -> List[Dict[str, Any]]:
        """
        Get list of registered services with metadata.

        Returns:
            List of service dictionaries with metadata

        Example:
            >>> discovery = ServiceDiscovery()
            >>> services = discovery.get_registered_services()
            >>> services[0]
            {
                'name': 'myapp.UserService',
                'full_name': '/myapp.UserService',
                'methods': ['GetUser', 'ListUsers'],
                'description': 'User management service',
                'file_path': 'apps/myapp/grpc_services.py',
                'class_name': 'UserService'
            }
        """
        services_metadata = []
        discovered_services = self.discover_services()

        for service_class, add_to_server_func in discovered_services:
            metadata = self._extract_service_metadata(service_class)
            if metadata:
                services_metadata.append(metadata)

        return services_metadata

    def get_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get service metadata by name.

        Args:
            service_name: Service name (e.g., 'myapp.UserService')

        Returns:
            Service metadata dictionary or None

        Example:
            >>> discovery = ServiceDiscovery()
            >>> service = discovery.get_service_by_name('myapp.UserService')
            >>> service['methods']
            ['GetUser', 'ListUsers', 'CreateUser']
        """
        services = self.get_registered_services()
        for service in services:
            if service.get('name') == service_name:
                return service
        return None

    def _extract_service_metadata(self, service_class: Any) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a service class.

        Args:
            service_class: gRPC service class

        Returns:
            Service metadata dictionary

        """
        try:
            class_name = service_class.__name__
            module_name = service_class.__module__

            # Extract service name (usually ClassName without 'Service' suffix)
            service_name = class_name
            if service_name.endswith('Service'):
                service_name = service_name[:-7]  # Remove 'Service' suffix

            # Build full service name
            # Try to get package from module name
            package = module_name.split('.')[0] if module_name else ''
            full_name = f"/{package}.{service_name}"

            # Extract methods
            methods = []
            for attr_name in dir(service_class):
                if attr_name.startswith('_'):
                    continue
                attr = getattr(service_class, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    # Check if it's likely a gRPC method (not internal Django/Python method)
                    if attr_name not in ['as_servicer', 'add_to_server', 'save', 'delete']:
                        methods.append(attr_name)

            # Get description from docstring
            description = ''
            if service_class.__doc__:
                description = service_class.__doc__.strip().split('\n')[0]

            # Get file path
            file_path = ''
            if hasattr(service_class, '__module__'):
                try:
                    module = importlib.import_module(service_class.__module__)
                    if hasattr(module, '__file__'):
                        file_path = module.__file__ or ''
                except Exception:
                    pass

            return {
                'name': f"{package}.{class_name}",
                'full_name': full_name,
                'methods': methods,
                'description': description,
                'file_path': file_path,
                'class_name': class_name,
                'base_class': service_class.__bases__[0].__name__ if service_class.__bases__ else '',
            }

        except Exception as e:
            logger.error(f"Error extracting metadata from {service_class}: {e}", exc_info=True)
            return None

    def get_handlers_hooks(self) -> List[Any]:
        """
        Get the handlers hook function(s) from config.

        Returns:
            List of handlers hook functions (empty list if none)

        Example:
            >>> discovery = ServiceDiscovery()
            >>> handlers_hooks = discovery.get_handlers_hooks()
            >>> for hook in handlers_hooks:
            ...     hook(server)
        """
        logger.warning(f"🔍 get_handlers_hooks called")
        if not self.config:
            logger.warning("❌ No gRPC config available")
            return []

        handlers_hook_paths = self.config.handlers_hook
        logger.warning(f"🔍 handlers_hook_paths = '{handlers_hook_paths}'")

        # Convert single string to list
        if isinstance(handlers_hook_paths, str):
            if not handlers_hook_paths:
                logger.debug("No handlers_hook configured")
                return []
            handlers_hook_paths = [handlers_hook_paths]

        hooks = []
        for handlers_hook_path in handlers_hook_paths:
            # Resolve {ROOT_URLCONF} placeholder
            if "{ROOT_URLCONF}" in handlers_hook_path:
                try:
                    from django.conf import settings
                    root_urlconf = settings.ROOT_URLCONF
                    handlers_hook_path = handlers_hook_path.replace("{ROOT_URLCONF}", root_urlconf)
                    logger.debug(f"Resolved handlers_hook: {handlers_hook_path}")
                except Exception as e:
                    logger.warning(f"Could not resolve {{ROOT_URLCONF}}: {e}")
                    continue

            try:
                # Import the module containing the hook
                module_path, func_name = handlers_hook_path.rsplit(".", 1)
                module = importlib.import_module(module_path)

                # Get the hook function
                handlers_hook = getattr(module, func_name)

                if not callable(handlers_hook):
                    logger.warning(f"handlers_hook {handlers_hook_path} is not callable")
                    continue

                logger.info(f"Loaded handlers hook: {handlers_hook_path}")
                hooks.append(handlers_hook)

            except ImportError as e:
                logger.warning(f"Failed to import handlers hook module {handlers_hook_path}: {e}")
                continue
            except AttributeError as e:
                logger.warning(f"Handlers hook function not found in {handlers_hook_path}: {e}")
                logger.debug(f"This is optional - the hook function does not exist")
                continue
            except Exception as e:
                logger.error(
                    f"Error loading handlers hook {handlers_hook_path}: {e}",
                    exc_info=True,
                )
                continue

        return hooks


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
        from django_cfg.apps.integrations.grpc.services.discovery import discover_and_register_services

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

    # Try handlers hooks first (can be multiple)
    handlers_hooks = discovery.get_handlers_hooks()
    for hook in handlers_hooks:
        try:
            hook(server)
            logger.info(f"Successfully called handlers hook: {hook.__name__}")
            count += 1  # We don't know exact count, but at least 1
        except Exception as e:
            logger.error(f"Error calling handlers hook {hook.__name__}: {e}", exc_info=True)

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
