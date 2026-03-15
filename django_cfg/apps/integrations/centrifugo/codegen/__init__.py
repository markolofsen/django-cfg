"""
Centrifugo WebSocket Client Code Generation.

Generates type-safe Python, TypeScript, and Go clients from Pydantic models.
Supports IntEnum to TypeScript/Swift/Go enum generation.
"""

from .discovery import (
    RPCMethodInfo,
    discover_rpc_methods_from_router,
    extract_all_models,
    extract_enums_from_module,
    extract_enums_from_models,
    get_method_summary,
)

__all__ = [
    "RPCMethodInfo",
    "discover_rpc_methods_from_router",
    "extract_all_models",
    "extract_enums_from_module",
    "extract_enums_from_models",
    "get_method_summary",
]
