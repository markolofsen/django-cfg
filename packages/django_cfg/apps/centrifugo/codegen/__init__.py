"""
Centrifugo WebSocket Client Code Generation.

Generates type-safe Python, TypeScript, and Go clients from Pydantic models.
"""

from .discovery import (
    RPCMethodInfo,
    discover_rpc_methods_from_router,
    extract_all_models,
    get_method_summary,
)

__all__ = [
    "RPCMethodInfo",
    "discover_rpc_methods_from_router",
    "extract_all_models",
    "get_method_summary",
]
