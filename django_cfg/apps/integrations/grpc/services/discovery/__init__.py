"""
gRPC service discovery and registry.

This package provides tools for discovering and registering gRPC services
in a distributed environment.

**Components**:
- service_discovery: Service discovery class
- registration: Service registration function
- service_registry: Service registry manager
- statistics: Statistics calculations
- utils: Utility functions

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.discovery import (
    ServiceDiscovery,
    ServiceRegistryManager,
    discover_and_register_services,
)

# Discover and register services
server = grpc.server(...)
count, names = discover_and_register_services(server)

# Access registry
registry = ServiceRegistryManager()
services = registry.get_all_services()
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

from .service_discovery import ServiceDiscovery
from .registration import discover_and_register_services, GRPCServer
from .service_registry import ServiceRegistryManager
from .statistics import (
    calculate_percentiles,
    get_service_statistics,
    aget_service_statistics,
    get_method_statistics,
    aget_method_statistics,
)
from .utils import (
    is_grpc_service,
    get_add_to_server_func,
    extract_service_name,
    extract_service_metadata,
)

__all__ = [
    # Main classes
    "ServiceDiscovery",
    "ServiceRegistryManager",
    # Registration
    "discover_and_register_services",
    "GRPCServer",
    # Statistics
    "calculate_percentiles",
    "get_service_statistics",
    "aget_service_statistics",
    "get_method_statistics",
    "aget_method_statistics",
    # Utils
    "is_grpc_service",
    "get_add_to_server_func",
    "extract_service_name",
    "extract_service_metadata",
]
