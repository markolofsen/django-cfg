"""
Utility functions for gRPC service discovery.
"""

import importlib
from typing import Any, Optional

from django_cfg.utils import get_logger

logger = get_logger("grpc.discovery.utils")

# Optional django-grpc-framework support
try:
    from django_grpc_framework import generics
    HAS_DJANGO_GRPC_FRAMEWORK = True
except ImportError:
    HAS_DJANGO_GRPC_FRAMEWORK = False
    generics = None
    logger.debug("django-grpc-framework not installed")


def is_grpc_service(obj: Any) -> bool:
    """
    Check if object is a gRPC service class.

    Args:
        obj: Object to check

    Returns:
        True if object is a gRPC service class
    """
    if not isinstance(obj, type):
        return False

    # Check for django-grpc-framework service
    if HAS_DJANGO_GRPC_FRAMEWORK and generics:
        try:
            if issubclass(obj, (
                generics.Service,
                generics.ModelService,
                generics.ReadOnlyModelService,
            )):
                return True
        except (TypeError, AttributeError):
            pass

    # Check for grpc servicer (has add_to_server method)
    if hasattr(obj, "add_to_server") and callable(getattr(obj, "add_to_server")):
        return True

    return False


def get_add_to_server_func(service_class: Any, module_path: str) -> Optional[Any]:
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
    try:
        base_module = module_path.rsplit(".", 1)[0]
        pb2_grpc_module_name = f"{base_module}_pb2_grpc"
        pb2_grpc_module = importlib.import_module(pb2_grpc_module_name)

        func_name = f"add_{service_class.__name__}_to_server"
        if hasattr(pb2_grpc_module, func_name):
            return getattr(pb2_grpc_module, func_name)

    except ImportError:
        logger.debug(f"No _pb2_grpc module found for {module_path}")
    except Exception as e:
        logger.debug(f"Error finding add_to_server for {service_class.__name__}: {e}")

    return None


def extract_service_name(service_class: Any) -> str:
    """
    Extract full service name from service class.

    Args:
        service_class: gRPC service class

    Returns:
        Full service name (e.g., 'trading_bots.BotStreamingService')
    """
    if hasattr(service_class, 'GRPC_SERVICE_NAME'):
        return service_class.GRPC_SERVICE_NAME

    if hasattr(service_class, '__module__'):
        module_parts = service_class.__module__.split('.')
        package = module_parts[0] if module_parts else 'unknown'

        # Find 'grpc' and use part BEFORE it as package
        try:
            grpc_idx = module_parts.index('grpc')
            if grpc_idx > 0:
                package = module_parts[grpc_idx - 1]
        except ValueError:
            # No 'grpc' in path
            for part in module_parts:
                if part in ('signals', 'streaming'):
                    package = part
                    break

        return f"{package}.{service_class.__name__}"

    return f"unknown.{service_class.__name__}"


def extract_service_metadata(service_class: Any) -> Optional[dict]:
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

        # Extract service name
        service_name = class_name
        if service_name.endswith('Service'):
            service_name = service_name[:-7]

        # Build full service name
        package = module_name.split('.')[0] if module_name else ''
        full_name = f"/{package}.{service_name}"

        # Extract methods
        methods = []
        for attr_name in dir(service_class):
            if attr_name.startswith('_'):
                continue
            attr = getattr(service_class, attr_name)
            if callable(attr) and attr_name not in ['as_servicer', 'add_to_server', 'save', 'delete']:
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


__all__ = [
    "is_grpc_service",
    "get_add_to_server_func",
    "extract_service_name",
    "extract_service_metadata",
    "HAS_DJANGO_GRPC_FRAMEWORK",
]
