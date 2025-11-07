"""
gRPC service discovery and registry.

This package provides tools for discovering and registering gRPC services
in a distributed environment.

**Components**:
- discovery: Service discovery mechanisms
- registry: Service registration and management

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.discovery import (
    ServiceDiscovery,
    ServiceRegistry,
)

# Register service
registry = ServiceRegistry()
registry.register(service_name="my-service", host="localhost", port=50051)

# Discover services
discovery = ServiceDiscovery()
services = discovery.discover_all()
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

# Export discovery components
from .discovery import ServiceDiscovery, discover_and_register_services
from .registry import ServiceRegistryManager

__all__ = [
    'ServiceDiscovery',
    'ServiceRegistryManager',
    'discover_and_register_services',
]
