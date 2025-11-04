"""
gRPC services utilities.

Provides service discovery, base classes, config helpers, service registry,
monitoring, and testing services for gRPC.
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
from .grpc_client import DynamicGRPCClient
from .monitoring_service import MonitoringService
from .proto_files_manager import ProtoFilesManager
from .service_registry import ServiceRegistryManager
from .testing_service import TestingService

__all__ = [
    "BaseService",
    "ReadOnlyService",
    "AuthRequiredService",
    "ServiceDiscovery",
    "discover_and_register_services",
    "ServiceRegistryManager",
    "MonitoringService",
    "TestingService",
    "DynamicGRPCClient",
    "ProtoFilesManager",
    "get_grpc_config",
    "get_grpc_config_or_default",
    "is_grpc_enabled",
    "get_grpc_server_config",
    "get_grpc_auth_config",
    "get_enabled_apps",
]
