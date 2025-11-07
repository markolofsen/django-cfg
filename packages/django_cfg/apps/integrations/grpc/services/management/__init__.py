"""
gRPC service management utilities.

This package provides tools for managing protobuf files, configuration,
and service lifecycle.

**Components**:
- proto_manager: Protobuf file management and compilation
- config_helper: Configuration utilities for gRPC services

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.management import (
    ProtoFilesManager,
    ConfigHelper,
)

# Manage proto files
proto_mgr = ProtoFilesManager()
proto_mgr.compile_all()

# Configuration helpers
config = ConfigHelper.get_grpc_config()
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

# Export when modules are refactored
# from .proto_manager import ProtoFilesManager
# from .config_helper import ConfigHelper

__all__ = [
    # 'ProtoFilesManager',
    # 'ConfigHelper',
]
