"""
Cross-process command routing for Django multi-process architecture.

This package provides automatic routing between direct calls (same process)
and gRPC calls (cross-process) for scenarios where Django runs multiple processes
(e.g., runserver + rungrpc).

**Components**:
- router: CrossProcessCommandRouter implementation
- CrossProcessConfig: Pydantic configuration model

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.routing import (
    CrossProcessCommandRouter,
    CrossProcessConfig,
)

# Configure router
config = CrossProcessConfig(
    grpc_host="localhost",
    grpc_port=50051,
    rpc_method_name="SendCommandToClient",
)

# Create router with factories
router = CrossProcessCommandRouter(
    config=config,
    get_service_instance=lambda: get_global_service(),
    stub_factory=create_grpc_stub,
    request_factory=create_request,
    extract_success=lambda r: r.success,
)

# Route commands (automatically chooses direct vs gRPC)
await router.send_command("client_123", command_pb)
```

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

# Config can be imported directly (no grpc dependency)
from .config import CrossProcessConfig

# Lazy import for router (requires grpc)
def __getattr__(name):
    """Lazy import router to avoid grpc dependency."""
    if name == 'CrossProcessCommandRouter':
        from .router import CrossProcessCommandRouter
        return CrossProcessCommandRouter
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    'CrossProcessConfig',
    'CrossProcessCommandRouter',
]
