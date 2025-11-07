"""
Utilities for gRPC Integration.

Reusable utilities for gRPC services in django-cfg.

**Available Modules**:
- streaming_logger: Rich logging for gRPC streams
- converters: Protobuf ↔ Python conversions (Pydantic configured)
- handlers: gRPC handler factory utilities

**Quick Imports**:
```python
from django_cfg.apps.integrations.grpc.utils import (
    # Logging
    setup_streaming_logger,
    get_streaming_logger,

    # Converters
    ProtobufConverterMixin,
    ConverterConfig,

    # Handlers
    create_grpc_handler,
)
```
"""

from .streaming_logger import setup_streaming_logger, get_streaming_logger
from .converters import (
    ConverterConfig,
    ProtobufConverterMixin,
    datetime_to_timestamp,
    timestamp_to_datetime,
    dict_to_struct,
    struct_to_dict,
)
from .handlers import (
    create_grpc_handler,
    create_multiple_grpc_handlers,
    validate_grpc_handler,
    validate_grpc_handlers,
)

__all__ = [
    # Logging
    "setup_streaming_logger",
    "get_streaming_logger",

    # Converters - Config
    "ConverterConfig",

    # Converters - Mixin
    "ProtobufConverterMixin",

    # Converters - Standalone functions
    "datetime_to_timestamp",
    "timestamp_to_datetime",
    "dict_to_struct",
    "struct_to_dict",

    # Handlers
    "create_grpc_handler",
    "create_multiple_grpc_handlers",
    "validate_grpc_handler",
    "validate_grpc_handlers",
]
