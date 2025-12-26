"""
Django-CFG Centrifugo Integration.

Provides Django integration with Centrifugo WebSocket server for real-time
notifications with delivery confirmation (ACK tracking).

Main Components:
- CentrifugoClient: Django client for publishing messages
- CentrifugoLog: Model for tracking publish operations
- CentrifugoLogger: Helper for automatic logging
- DjangoCfgCentrifugoConfig: Pydantic configuration model

Example:
    >>> from django_cfg.apps.integrations.centrifugo import get_centrifugo_client
    >>>
    >>> client = get_centrifugo_client()
    >>> result = await client.publish_with_ack(
    ...     channel="user#123",
    ...     data={"title": "Hello", "message": "World"},
    ...     ack_timeout=10
    ... )
    >>> print(f"Delivered: {result.delivered}")
"""

from .services.client.client import CentrifugoClient, get_centrifugo_client, PublishResponse
from .services.client.direct_client import DirectCentrifugoClient
from .services.client.config import DjangoCfgCentrifugoConfig
from .services.client.exceptions import (
    CentrifugoBaseException,
    CentrifugoConfigurationError,
    CentrifugoConnectionError,
    CentrifugoPublishError,
    CentrifugoTimeoutError,
    CentrifugoValidationError,
)
from .services.logging import CentrifugoLogContext, CentrifugoLogger
from .decorators import websocket_rpc, centrifugo_channel
from .registry import (
    get_global_registry,
    get_global_channel_registry,
    RegisteredHandler,
    RegisteredChannel,
)

# Note: CentrifugoLog model is not imported here to avoid AppRegistryNotReady errors
# Import it directly from .models when needed: from django_cfg.apps.integrations.centrifugo.models import CentrifugoLog

__all__ = [
    # Config
    "DjangoCfgCentrifugoConfig",
    # Client
    "CentrifugoClient",
    "DirectCentrifugoClient",
    "get_centrifugo_client",
    "PublishResponse",
    # Logging
    "CentrifugoLogger",
    "CentrifugoLogContext",
    # Exceptions
    "CentrifugoBaseException",
    "CentrifugoTimeoutError",
    "CentrifugoPublishError",
    "CentrifugoConnectionError",
    "CentrifugoConfigurationError",
    "CentrifugoValidationError",
    # Decorators
    "websocket_rpc",
    "centrifugo_channel",
    # Registry
    "get_global_registry",
    "get_global_channel_registry",
    "RegisteredHandler",
    "RegisteredChannel",
]
