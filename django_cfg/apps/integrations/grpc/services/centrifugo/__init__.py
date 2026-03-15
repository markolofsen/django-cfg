"""
gRPC → Centrifugo Integration.

Mixin and configuration for bridging gRPC streaming events to Centrifugo WebSocket.
"""

from .bridge import CentrifugoBridgeMixin
from .config import ChannelConfig, CentrifugoChannels
from .demo import (
    DemoChannels,
    DemoBridgeService,
    test_complete_integration,
    test_demo_service,
    send_demo_event,
)

__all__ = [
    # Core components
    "CentrifugoBridgeMixin",
    "ChannelConfig",
    "CentrifugoChannels",

    # Demo/testing
    "DemoChannels",
    "DemoBridgeService",
    "test_complete_integration",
    "test_demo_service",
    "send_demo_event",
]
