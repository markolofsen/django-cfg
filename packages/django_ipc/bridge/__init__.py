"""
Redis Bridge for WebSocket Servers.

Provides RPC bridge to handle requests from Django via Redis IPC.
"""

from .bridge import RPCBridge

__all__ = ["RPCBridge"]
