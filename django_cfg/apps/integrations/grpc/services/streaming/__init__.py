"""
Universal bidirectional streaming components for gRPC.

This package provides generic, type-safe components for implementing
bidirectional gRPC streaming services with decomposed architecture.

Components:
- types: Protocol definitions for type-safe callbacks
- config: Pydantic v2 configuration models
- core: Low-level connection/registry/queue management
- processors: Input/output processing
- integrations: Centrifugo publisher and circuit breaker
- service: BidirectionalStreamingService implementation

Usage Example:
```python
from django_cfg.apps.integrations.grpc.services.streaming import (
    BidirectionalStreamingService,
    BidirectionalStreamingConfig,
    ConfigPresets,
    MessageProcessor,
    ClientIdExtractor,
    PingMessageCreator,
)

# Use preset config
service = BidirectionalStreamingService(
    config=ConfigPresets.PRODUCTION,
    message_processor=my_processor,
    client_id_extractor=extract_id,
    ping_message_creator=create_ping,
)
```

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

# Type definitions
from .types import (
    # Type variables
    TMessage,
    TCommand,

    # Core protocols
    MessageProcessor,
    ClientIdExtractor,
    PingMessageCreator,

    # Connection protocols
    ConnectionCallback,
    ErrorHandler,

    # Connection info
    ConnectionInfo,
)

# Configuration
from .config import (
    # Enums
    StreamingMode,
    PingStrategy,

    # Models
    BidirectionalStreamingConfig,

    # Presets
    ConfigPresets,
)

# Core components (optional - usually not needed by users)
# from .core import ConnectionManager, ResponseRegistry, QueueManager

# Processors (optional - usually not needed by users)
# from .processors import InputProcessor, OutputProcessor

# Integrations (optional - usually not needed by users)
# from .integrations import CentrifugoPublisher, CentrifugoCircuitBreaker

# Service - lazy import to avoid grpc dependency
def __getattr__(name):
    """Lazy import BidirectionalStreamingService to avoid grpc dependency."""
    if name == 'BidirectionalStreamingService':
        from .service import BidirectionalStreamingService
        return BidirectionalStreamingService
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Type variables
    'TMessage',
    'TCommand',

    # Protocols
    'MessageProcessor',
    'ClientIdExtractor',
    'PingMessageCreator',
    'ConnectionCallback',
    'ErrorHandler',

    # Connection info
    'ConnectionInfo',

    # Enums
    'StreamingMode',
    'PingStrategy',

    # Configuration
    'BidirectionalStreamingConfig',
    'ConfigPresets',

    # Service
    'BidirectionalStreamingService',
]
