"""
Utilities for gRPC Integration.

Reusable utilities for gRPC services in django-cfg.

**Available Modules**:
- streaming_logger: Rich logging for gRPC streams
- converters: Protobuf ↔ Python conversions (Pydantic configured)
- handlers: gRPC handler factory utilities
- betterproto_compiler: Betterproto2 compilation utilities

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

    # Betterproto2 Compilation
    compile_proto,
    compile_protos_directory,
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

# Betterproto2 compiler (optional)
try:
    from .betterproto_compiler import (
        is_betterproto2_available,
        is_protoc_available,
        get_protoc_version,
        BetterprotoCompilerConfig,
        BetterprotoCompiler,
        Betterproto2DirectCompiler,
        compile_proto,
        compile_protos_directory,
        compile_betterproto2,
    )
    _has_betterproto_compiler = True
except ImportError:
    _has_betterproto_compiler = False
    is_betterproto2_available = None
    is_protoc_available = None
    get_protoc_version = None
    BetterprotoCompilerConfig = None
    BetterprotoCompiler = None
    Betterproto2DirectCompiler = None
    compile_proto = None
    compile_protos_directory = None
    compile_betterproto2 = None

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

    # Betterproto2 Compilation
    "is_betterproto2_available",
    "is_protoc_available",
    "get_protoc_version",
    "BetterprotoCompilerConfig",
    "BetterprotoCompiler",
    "Betterproto2DirectCompiler",
    "compile_proto",
    "compile_protos_directory",
    "compile_betterproto2",
]
