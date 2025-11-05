"""
Centrifugo Client.

Two client implementations:
- CentrifugoClient: Via wrapper (for external API, with auth & logging)
- DirectCentrifugoClient: Direct to Centrifugo (for internal use, lightweight)
"""

from .client import CentrifugoClient, PublishResponse, get_centrifugo_client
from .config import DjangoCfgCentrifugoConfig
from .direct_client import DirectCentrifugoClient, get_direct_centrifugo_client
from .exceptions import (
    CentrifugoBaseException,
    CentrifugoConfigurationError,
    CentrifugoConnectionError,
    CentrifugoPublishError,
    CentrifugoTimeoutError,
    CentrifugoValidationError,
)

__all__ = [
    "DjangoCfgCentrifugoConfig",
    "CentrifugoClient",
    "get_centrifugo_client",
    "DirectCentrifugoClient",
    "get_direct_centrifugo_client",
    "PublishResponse",
    "CentrifugoBaseException",
    "CentrifugoTimeoutError",
    "CentrifugoPublishError",
    "CentrifugoConnectionError",
    "CentrifugoConfigurationError",
    "CentrifugoValidationError",
]
