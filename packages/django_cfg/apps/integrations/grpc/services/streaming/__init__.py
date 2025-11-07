"""
Universal bidirectional streaming components for gRPC.

This package provides generic, type-safe components for implementing
bidirectional gRPC streaming services.

**Components**:
- types: Protocol definitions for type-safe callbacks
- config: Pydantic v2 configuration models
- service: BidirectionalStreamingService implementation

**Usage Example**:
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

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
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

    # Type aliases
    MessageProcessorType,
    ClientIdExtractorType,
    PingMessageCreatorType,

    # Validation
    is_valid_message_processor,
    is_valid_client_id_extractor,
    is_valid_ping_creator,
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

    # Type aliases
    'MessageProcessorType',
    'ClientIdExtractorType',
    'PingMessageCreatorType',

    # Validation functions
    'is_valid_message_processor',
    'is_valid_client_id_extractor',
    'is_valid_ping_creator',

    # Enums
    'StreamingMode',
    'PingStrategy',

    # Configuration
    'BidirectionalStreamingConfig',
    'ConfigPresets',

    # Service
    'BidirectionalStreamingService',
]
