"""
Django-CFG RPC Client Module.

Lightweight synchronous RPC client for Django applications to communicate
with django-cfg-rpc WebSocket servers via Redis.

Key Features:
- ✅ 100% synchronous (no async/await in Django)
- ✅ Type-safe with Pydantic 2 models from django-cfg-rpc
- ✅ Automatic connection pooling
- ✅ Optional dependency on django-cfg-rpc
- ✅ Graceful fallback if django-cfg-rpc not installed

Example:
    >>> from django_cfg.modules.django_ipc_client import get_rpc_client
    >>> from django_ipc.models import NotificationRequest, NotificationResponse
    >>>
    >>> rpc = get_rpc_client()
    >>> result: NotificationResponse = rpc.call(
    ...     method="send_notification",
    ...     params=NotificationRequest(
    ...         user_id="123",
    ...         type="order_update",
    ...         title="Order Confirmed",
    ...         message="Your order has been confirmed"
    ...     ),
    ...     result_model=NotificationResponse
    ... )
"""

from .services.client.client import DjangoCfgRPCClient, get_rpc_client
from .services.client.config import DjangoCfgRPCConfig
from .services.client.exceptions import (
    RPCConfigurationError,
    RPCConnectionError,
    RPCRemoteError,
    RPCTimeoutError,
)

__all__ = [
    # Client
    "DjangoCfgRPCClient",
    "get_rpc_client",
    # Configuration
    "DjangoCfgRPCConfig",
    # Exceptions
    "RPCTimeoutError",
    "RPCRemoteError",
    "RPCConnectionError",
    "RPCConfigurationError",
]
