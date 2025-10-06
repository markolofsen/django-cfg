"""
Code generation utilities for django_ipc.

Auto-generates TypeScript and Python WebSocket clients from RPC server handlers.
"""

from .discovery import discover_rpc_methods

__all__ = [
    'discover_rpc_methods',
]
