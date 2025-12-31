"""
gRPC client utilities for django-cfg.

This package provides tools for creating and managing gRPC client connections.

**Components**:
- DynamicGRPCClient: Dynamic client using reflection (no proto files needed)
- ResilientGRPCClient: Sync client with retry and circuit breaker
- AsyncResilientGRPCClient: Async client with retry and circuit breaker
- GRPCChannelPool: Async channel pool for connection reuse
- SyncGRPCChannelPool: Sync channel pool for connection reuse
- Betterproto2Client: Modern async client using betterproto2/grpclib

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.client import (
    DynamicGRPCClient,
    ResilientGRPCClient,
    get_channel_pool,
)

# Basic usage
client = DynamicGRPCClient(host="localhost", port=50051)
response = client.call_method("api.Service", "Method", {"key": "value"})

# With resilience (retry + circuit breaker)
with ResilientGRPCClient(host="localhost", port=50051) as client:
    response = client.call_method("api.Service", "Method", {"key": "value"})

# With connection pooling (async)
pool = get_channel_pool()
async with pool.pooled_channel("localhost:50051") as channel:
    # use channel...
    pass

# With betterproto2 (requires grpclib)
from django_cfg.apps.integrations.grpc.services.client import Betterproto2Client
from mypackage import MyServiceStub, MyRequest

async with Betterproto2Client(host="localhost", port=50051) as client:
    stub = client.get_stub(MyServiceStub)
    response = await stub.my_method(MyRequest(field="value"))
```

Created: 2025-11-07
Updated: 2025-12-31 - Added resilient clients, connection pooling, and betterproto2 support
Status: %%PRODUCTION%%
"""

from .client import DynamicGRPCClient
from .resilient import ResilientGRPCClient, AsyncResilientGRPCClient
from .pool import (
    GRPCChannelPool,
    SyncGRPCChannelPool,
    PoolConfig,
    get_channel_pool,
    get_sync_channel_pool,
    close_global_pool,
    close_global_sync_pool,
)

# Betterproto2 client (optional, requires grpclib)
try:
    from .betterproto_client import (
        Betterproto2Client,
        Betterproto2ChannelPool,
        ResilientStubWrapper,
        get_betterproto_pool,
        close_betterproto_pool,
        HAS_GRPCLIB,
    )
    _has_betterproto = True
except ImportError:
    Betterproto2Client = None
    Betterproto2ChannelPool = None
    ResilientStubWrapper = None
    get_betterproto_pool = None
    close_betterproto_pool = None
    HAS_GRPCLIB = False
    _has_betterproto = False

__all__ = [
    # Clients
    "DynamicGRPCClient",
    "ResilientGRPCClient",
    "AsyncResilientGRPCClient",
    # Pool
    "GRPCChannelPool",
    "SyncGRPCChannelPool",
    "PoolConfig",
    "get_channel_pool",
    "get_sync_channel_pool",
    "close_global_pool",
    "close_global_sync_pool",
    # Betterproto2 (optional)
    "Betterproto2Client",
    "Betterproto2ChannelPool",
    "ResilientStubWrapper",
    "get_betterproto_pool",
    "close_betterproto_pool",
    "HAS_GRPCLIB",
]
