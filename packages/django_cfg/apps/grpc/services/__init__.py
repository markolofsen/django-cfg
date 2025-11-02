"""
gRPC services utilities.

Provides service discovery, base classes, and config helpers for gRPC services.
"""

from .base import AuthRequiredService, BaseService, ReadOnlyService
from .config_helper import (
    get_enabled_apps,
    get_grpc_auth_config,
    get_grpc_config,
    get_grpc_config_or_default,
    get_grpc_server_config,
    is_grpc_enabled,
)
from .discovery import ServiceDiscovery, discover_and_register_services

__all__ = [
    "BaseService",
    "ReadOnlyService",
    "AuthRequiredService",
    "ServiceDiscovery",
    "discover_and_register_services",
    "get_grpc_config",
    "get_grpc_config_or_default",
    "is_grpc_enabled",
    "get_grpc_server_config",
    "get_grpc_auth_config",
    "get_enabled_apps",
]
