"""
gRPC client utilities for django-cfg.

This package provides tools for creating and managing gRPC client connections.

**Components**:
- client: GrpcClient for service-to-service communication

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.client import GrpcClient

client = GrpcClient(host="localhost", port=50051)
# Use client for gRPC calls
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

# Export when client module is refactored
# from .client import GrpcClient

__all__ = [
    # 'GrpcClient',  # Uncomment when ready
]
