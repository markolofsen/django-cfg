"""
gRPC services utilities.

Provides organized gRPC service components:
- **streaming**: Universal bidirectional streaming (NEW)
- **routing**: Cross-process command routing (NEW)
- **client**: gRPC client utilities
- **discovery**: Service discovery and registry
- **management**: Proto files and config management
- **monitoring**: Service monitoring and testing
- **rendering**: Content generation (charts, etc.)
- **base**: Base service classes

**Quick Imports**:
```python
# New universal components
from django_cfg.apps.integrations.grpc.services.streaming import (
    BidirectionalStreamingService,
    ConfigPresets,
)

from django_cfg.apps.integrations.grpc.services.routing import (
    CrossProcessCommandRouter,
    CrossProcessConfig,
)

# Existing services
from django_cfg.apps.integrations.grpc.services import (
    BaseService,
    ServiceDiscovery,
)
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

# Lazy imports to avoid Django initialization on import
# Import only when actually accessed via __getattr__

def __getattr__(name):
    """Lazy import to avoid Django setup on package import."""

    # Base service classes
    if name in ('AuthRequiredService', 'BaseService', 'ReadOnlyService'):
        from .base import AuthRequiredService, BaseService, ReadOnlyService
        return locals()[name]

    # Management utilities
    if name in ('get_enabled_apps', 'get_grpc_auth_config', 'get_grpc_config',
                'get_grpc_config_or_default', 'get_grpc_server_config', 'is_grpc_enabled'):
        from .management.config_helper import (
            get_enabled_apps,
            get_grpc_auth_config,
            get_grpc_config,
            get_grpc_config_or_default,
            get_grpc_server_config,
            is_grpc_enabled,
        )
        return locals()[name]

    if name == 'ProtoFilesManager':
        from .management.proto_manager import ProtoFilesManager
        return ProtoFilesManager

    # Discovery
    if name == 'ServiceDiscovery':
        from .discovery.service_discovery import ServiceDiscovery
        return ServiceDiscovery

    if name == 'discover_and_register_services':
        from .discovery.registration import discover_and_register_services
        return discover_and_register_services

    if name == 'ServiceRegistryManager':
        from .discovery.service_registry import ServiceRegistryManager
        return ServiceRegistryManager

    # Client
    if name == 'DynamicGRPCClient':
        from .client.client import DynamicGRPCClient
        return DynamicGRPCClient

    # Monitoring
    if name == 'MonitoringService':
        from .monitoring.monitoring import MonitoringService
        return MonitoringService

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Base classes
    "BaseService",
    "ReadOnlyService",
    "AuthRequiredService",

    # Discovery
    "ServiceDiscovery",
    "discover_and_register_services",
    "ServiceRegistryManager",

    # Monitoring
    "MonitoringService",

    # Client
    "DynamicGRPCClient",

    # Management
    "ProtoFilesManager",
    "get_grpc_config",
    "get_grpc_config_or_default",
    "is_grpc_enabled",
    "get_grpc_server_config",
    "get_grpc_auth_config",
    "get_enabled_apps",

    # New components available via subpackages:
    # - streaming: BidirectionalStreamingService, ConfigPresets, etc.
    # - routing: CrossProcessCommandRouter, CrossProcessConfig
]
