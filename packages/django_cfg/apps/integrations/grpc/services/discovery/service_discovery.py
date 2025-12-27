"""
Service Discovery for gRPC.

Automatically discovers and registers gRPC services from Django apps.
"""

import importlib
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps

from django_cfg.utils import get_logger

from ..management.config_helper import get_grpc_config
from .utils import (
    is_grpc_service,
    get_add_to_server_func,
    extract_service_metadata,
)

logger = get_logger("grpc.discovery")


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
        self.config = get_grpc_config()

        if self.config:
            self.auto_register = self.config.auto_register_apps
            self.enabled_apps = self.config.enabled_apps if self.config.auto_register_apps else []
            self.custom_services = self.config.custom_services
        else:
            self.auto_register = False
            self.enabled_apps = []
            self.custom_services = {}
            logger.warning("gRPC config not found, service discovery disabled")

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
        """
        discovered_services = []

        if self.auto_register:
            for app_label in self.enabled_apps:
                services = self._discover_app_services(app_label)
                discovered_services.extend(services)

        for service_path in self.custom_services.values():
            service = self._load_custom_service(service_path)
            if service:
                discovered_services.append(service)

        logger.info(f"Discovered {len(discovered_services)} gRPC service(s)")
        return discovered_services

    def _discover_app_services(self, app_label: str) -> List[Tuple[Any, Any]]:
        """Discover services from a Django app."""
        services = []

        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            logger.warning(
                f"[gRPC Discovery] App '{app_label}' not found in INSTALLED_APPS. "
                f"Either add it to INSTALLED_APPS or remove from grpc.enabled_apps in config"
            )
            return services

        for module_name in self.service_modules:
            full_module_path = f"{app_config.name}.{module_name}"

            try:
                module = importlib.import_module(full_module_path)
                logger.debug(f"Found gRPC module: {full_module_path}")

                app_services = self._extract_services_from_module(module, full_module_path)
                services.extend(app_services)

            except ImportError:
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
        """Extract gRPC services from a module."""
        services = []

        # Look for grpc_handlers() function
        if hasattr(module, "grpc_handlers"):
            handlers_func = getattr(module, "grpc_handlers")
            if callable(handlers_func):
                try:
                    handlers = handlers_func(None)
                    logger.info(f"Found grpc_handlers() in {module_path}")

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
            if attr_name.startswith("_"):
                continue

            attr = getattr(module, attr_name)

            if is_grpc_service(attr):
                logger.debug(f"Found gRPC service class: {module_path}.{attr_name}")

                add_to_server_func = get_add_to_server_func(attr, module_path)
                if add_to_server_func:
                    services.append((attr, add_to_server_func))

        return services

    def _load_custom_service(self, service_path: str) -> Optional[Tuple[Any, Any]]:
        """Load a custom service from dotted path."""
        try:
            module_path, class_name = service_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            service_class = getattr(module, class_name)

            add_to_server_func = get_add_to_server_func(service_class, module_path)
            if not add_to_server_func:
                logger.warning(f"Custom service {service_path} has no add_to_server function")
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
        """Get list of registered services with metadata."""
        services_metadata = []
        discovered_services = self.discover_services()

        for service_class, add_to_server_func in discovered_services:
            metadata = extract_service_metadata(service_class)
            if metadata:
                services_metadata.append(metadata)

        return services_metadata

    def get_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service metadata by name."""
        services = self.get_registered_services()
        for service in services:
            if service.get('name') == service_name:
                return service
        return None

    def get_handlers_hooks(self) -> List[Any]:
        """Get the handlers hook function(s) from config."""
        logger.info(f"get_handlers_hooks: config={self.config}")

        if not self.config:
            logger.warning("No gRPC config available for handlers_hooks")
            return []

        handlers_hook_paths = self.config.handlers_hook
        logger.info(f"get_handlers_hooks: handlers_hook_paths={handlers_hook_paths}")

        if isinstance(handlers_hook_paths, str):
            if not handlers_hook_paths:
                logger.debug("No handlers_hook configured")
                return []
            handlers_hook_paths = [handlers_hook_paths]

        hooks = []
        for handlers_hook_path in handlers_hook_paths:
            hook = self._load_handler_hook(handlers_hook_path)
            if hook:
                hooks.append(hook)

        return hooks

    def _load_handler_hook(self, handlers_hook_path: str) -> Optional[Any]:
        """Load a single handler hook."""
        # Resolve {ROOT_URLCONF} placeholder
        if "{ROOT_URLCONF}" in handlers_hook_path:
            try:
                from django.conf import settings
                root_urlconf = settings.ROOT_URLCONF
                handlers_hook_path = handlers_hook_path.replace("{ROOT_URLCONF}", root_urlconf)
                logger.debug(f"Resolved handlers_hook: {handlers_hook_path}")
            except Exception as e:
                logger.warning(f"Could not resolve {{ROOT_URLCONF}}: {e}")
                return None

        try:
            module_path, func_name = handlers_hook_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            handlers_hook = getattr(module, func_name)

            if not callable(handlers_hook):
                logger.warning(f"handlers_hook {handlers_hook_path} is not callable")
                return None

            logger.info(f"Loaded handlers hook: {handlers_hook_path}")
            return handlers_hook

        except ImportError as e:
            logger.warning(f"Failed to import handlers hook module {handlers_hook_path}: {e}")
            return None
        except AttributeError as e:
            logger.warning(f"Handlers hook function not found in {handlers_hook_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading handlers hook {handlers_hook_path}: {e}", exc_info=True)
            return None


__all__ = ["ServiceDiscovery"]
