"""
gRPC client utilities for django-cfg.

This package provides tools for creating and managing gRPC client connections.

**Components**:
- DynamicGRPCClient: Dynamic client using reflection (no proto files needed)

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.client import DynamicGRPCClient

client = DynamicGRPCClient(host="localhost", port=50051)
response = client.invoke_method("api.Service", "Method", {"key": "value"})
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

from .client import DynamicGRPCClient

__all__ = [
    "DynamicGRPCClient",
]
