"""
Django RPC Module for WebSocket Communication.

Provides synchronous RPC client for Django applications to communicate
with external WebSocket servers via Redis.

Example:
    >>> from django_cfg.modules.django_rpc import get_rpc_client
    >>> from django_cfg.models.websocket import NotificationRequest, NotificationResponse
    >>>
    >>> rpc = get_rpc_client()
    >>> result: NotificationResponse = rpc.call(
    ...     method="send_notification",
    ...     params=NotificationRequest(user_id="123", message="Hello"),
    ...     result_model=NotificationResponse
    ... )
"""

from .client import WebSocketRPCClient, get_rpc_client
from .config import WebSocketRPCConfig
from .exceptions import (
    RPCTimeoutError,
    RPCRemoteError,
    RPCConnectionError,
    RPCConfigurationError,
)

__all__ = [
    # Client
    "WebSocketRPCClient",
    "get_rpc_client",
    # Configuration
    "WebSocketRPCConfig",
    # Exceptions
    "RPCTimeoutError",
    "RPCRemoteError",
    "RPCConnectionError",
    "RPCConfigurationError",
]
