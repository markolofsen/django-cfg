"""
Pydantic v2 configuration models for gRPC bidirectional streaming.

This module provides type-safe, validated configuration for bidirectional streaming services.
All models are frozen and use strict validation to prevent runtime errors.

**Design Principles**:
- 100% Pydantic v2 (no raw dicts)
- Frozen models (immutable)
- Strict validation with Field constraints
- extra='forbid' to catch typos
- Comprehensive documentation

**Usage Example**:
```python
config = BidirectionalStreamingConfig(
    ping_interval=5.0,
    ping_timeout=30.0,
    enable_sleep_zero=True,
    max_queue_size=1000
)

service = BidirectionalStreamingService(
    config=config,
    message_processor=process_messages,
    ...
)
```

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================================================
# Enumerations
# ============================================================================

class StreamingMode(str, Enum):
    """
    Streaming iteration modes for handling bidirectional streams.

    **Modes**:
        ASYNC_FOR: Use `async for message in stream` (simpler, automatic iteration)
        ANEXT: Use `await anext(stream)` (manual control, better error handling)

    **Comparison**:

    | Feature               | ASYNC_FOR | ANEXT |
    |-----------------------|-----------|-------|
    | Simplicity            | ✅ Simple | ⚠️ Manual |
    | Error Control         | ⚠️ Limited | ✅ Full |
    | Timeout Control       | ⚠️ Limited | ✅ Full |
    | Early Exit            | ⚠️ Limited | ✅ Easy |

    **Usage**:
    ```python
    # ASYNC_FOR mode
    config = BidirectionalStreamingConfig(streaming_mode=StreamingMode.ASYNC_FOR)
    # Implementation: async for message in stream: ...

    # ANEXT mode
    config = BidirectionalStreamingConfig(streaming_mode=StreamingMode.ANEXT)
    # Implementation: message = await anext(stream)
    ```

    **Recommendation**:
        - Use ASYNC_FOR for simple services
        - Use ANEXT for services requiring fine-grained control
    """

    ASYNC_FOR = "async_for"
    """Use async for iteration (automatic, simpler)"""

    ANEXT = "anext"
    """Use anext() calls (manual, more control)"""


class PingStrategy(str, Enum):
    """
    Strategies for sending ping/keepalive messages.

    **Strategies**:
        INTERVAL: Send ping every N seconds (time-based)
        ON_IDLE: Send ping only when no messages sent recently (activity-based)
        DISABLED: Don't send automatic pings (manual control)

    **Comparison**:

    | Strategy  | Network Usage | Responsiveness | Use Case |
    |-----------|---------------|----------------|----------|
    | INTERVAL  | ⚠️ Higher | ✅ Predictable | Critical services |
    | ON_IDLE   | ✅ Lower | ⚠️ Variable | Normal services |
    | DISABLED  | ✅ Minimal | ❌ Manual | Testing/debug |

    **Usage**:
    ```python
    # Send ping every 5 seconds
    config = BidirectionalStreamingConfig(
        ping_strategy=PingStrategy.INTERVAL,
        ping_interval=5.0
    )

    # Send ping only after 10 seconds of inactivity
    config = BidirectionalStreamingConfig(
        ping_strategy=PingStrategy.ON_IDLE,
        ping_interval=10.0
    )

    # No automatic pings
    config = BidirectionalStreamingConfig(
        ping_strategy=PingStrategy.DISABLED
    )
    ```
    """

    INTERVAL = "interval"
    """Send ping every N seconds regardless of activity"""

    ON_IDLE = "on_idle"
    """Send ping only after N seconds of inactivity"""

    DISABLED = "disabled"
    """Don't send automatic pings"""


# ============================================================================
# Configuration Models
# ============================================================================

class BidirectionalStreamingConfig(BaseModel):
    """
    Configuration for bidirectional gRPC streaming services.

    This model provides type-safe configuration with validation for all streaming parameters.
    All fields have sensible defaults based on production experience.

    **Core Parameters**:
        streaming_mode: How to iterate over input stream (ASYNC_FOR vs ANEXT)
        ping_strategy: When to send keepalive pings (INTERVAL vs ON_IDLE)
        ping_interval: Seconds between pings (must be > 0)
        ping_timeout: Max seconds to wait for ping response (must be >= ping_interval)

    **Queue Parameters**:
        max_queue_size: Max items in output queue before blocking (must be > 0)
        queue_timeout: Max seconds to wait when enqueuing to full queue

    **Advanced Parameters**:
        enable_sleep_zero: Enable `await asyncio.sleep(0)` for event loop yielding
        enable_centrifugo: Auto-publish to Centrifugo WebSocket channels
        enable_logging: Enable structured logging for stream events

    **Validation Rules**:
        - ping_timeout >= ping_interval (can't timeout before ping)
        - ping_interval > 0 (must be positive)
        - max_queue_size > 0 (must have capacity)
        - All timeouts must be positive

    **Example - Production Config**:
    ```python
    config = BidirectionalStreamingConfig(
        streaming_mode=StreamingMode.ANEXT,
        ping_strategy=PingStrategy.INTERVAL,
        ping_interval=5.0,
        ping_timeout=30.0,
        max_queue_size=1000,
        enable_sleep_zero=True,
        enable_centrifugo=True,
        enable_logging=True
    )
    ```

    **Example - Development Config**:
    ```python
    config = BidirectionalStreamingConfig(
        streaming_mode=StreamingMode.ASYNC_FOR,
        ping_strategy=PingStrategy.ON_IDLE,
        ping_interval=10.0,
        enable_centrifugo=False,
        enable_logging=True
    )
    ```
    """

    # ------------------------------------------------------------------------
    # Streaming Parameters
    # ------------------------------------------------------------------------

    streaming_mode: StreamingMode = Field(
        default=StreamingMode.ANEXT,
        description="How to iterate over input stream (ASYNC_FOR vs ANEXT)",
    )

    # ------------------------------------------------------------------------
    # Ping/Keepalive Parameters
    # ------------------------------------------------------------------------

    ping_strategy: PingStrategy = Field(
        default=PingStrategy.INTERVAL,
        description="When to send keepalive pings (INTERVAL vs ON_IDLE vs DISABLED)",
    )

    ping_interval: float = Field(
        default=5.0,
        gt=0.0,
        le=300.0,  # Max 5 minutes
        description="Seconds between pings (must be > 0, max 300)",
    )

    ping_timeout: Optional[float] = Field(
        default=None,
        gt=0.0,
        le=600.0,  # Max 10 minutes
        description="Max seconds to wait for ping response (None = 6x ping_interval)",
    )

    # ------------------------------------------------------------------------
    # Queue Parameters
    # ------------------------------------------------------------------------

    max_queue_size: int = Field(
        default=1000,
        gt=0,
        le=100000,  # Max 100k items
        description="Max items in output queue before blocking (must be > 0)",
    )

    queue_timeout: Optional[float] = Field(
        default=10.0,
        gt=0.0,
        le=60.0,  # Max 1 minute
        description="Max seconds to wait when enqueuing to full queue (None = no timeout)",
    )

    # ------------------------------------------------------------------------
    # Advanced Parameters
    # ------------------------------------------------------------------------

    enable_sleep_zero: bool = Field(
        default=True,
        description="Enable `await asyncio.sleep(0)` for event loop yielding (CRITICAL for responsiveness)",
    )

    enable_centrifugo: bool = Field(
        default=True,
        description="Auto-publish messages to Centrifugo WebSocket channels",
    )

    centrifugo_channel_prefix: str = Field(
        default="grpc",
        min_length=1,
        max_length=50,
        description="Prefix for auto-generated Centrifugo channels (e.g., 'grpc' → 'grpc#client_id#field_name')",
    )

    centrifugo_auto_publish_messages: bool = Field(
        default=True,
        description="Automatically publish ALL incoming protobuf messages to Centrifugo (no configuration needed)",
    )

    centrifugo_auto_publish_commands: bool = Field(
        default=True,
        description="Automatically publish ALL outgoing commands to Centrifugo (Django → Client direction)",
    )

    centrifugo_circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker for Centrifugo auto-publishing (prevents cascading failures)",
    )

    centrifugo_circuit_breaker_threshold: int = Field(
        default=5,
        gt=0,
        le=100,
        description="Max consecutive failures before opening circuit (default: 5)",
    )

    centrifugo_circuit_breaker_timeout: float = Field(
        default=60.0,
        gt=0.0,
        le=600.0,
        description="Seconds to wait in OPEN state before testing recovery (default: 60)",
    )

    enable_logging: bool = Field(
        default=True,
        description="Enable structured logging for stream events",
    )

    logger_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Logger name for auto-created logger (None = 'grpc_streaming')",
    )

    # ------------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------------

    connection_timeout: Optional[float] = Field(
        default=None,
        gt=0.0,
        le=3600.0,  # Max 1 hour
        description="Max seconds for entire connection (None = unlimited)",
    )

    max_consecutive_errors: int = Field(
        default=3,
        ge=0,
        le=100,
        description="Max consecutive errors before disconnecting (0 = unlimited)",
    )

    # ------------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------------

    @field_validator('ping_timeout')
    @classmethod
    def set_default_ping_timeout(cls, v: Optional[float], info) -> float:
        """
        Set ping_timeout to 6x ping_interval if not provided.

        This ensures reasonable timeout with safety margin.
        """
        if v is None:
            ping_interval = info.data.get('ping_interval', 5.0)
            return ping_interval * 6.0
        return v

    @model_validator(mode='after')
    def validate_timeout_relationship(self) -> 'BidirectionalStreamingConfig':
        """
        Ensure ping_timeout >= ping_interval.

        Can't timeout before next ping is due.
        """
        # ping_timeout is set by field_validator, so it should never be None here
        if self.ping_timeout is not None and self.ping_timeout < self.ping_interval:
            raise ValueError(
                f"ping_timeout ({self.ping_timeout}s) must be >= ping_interval ({self.ping_interval}s)"
            )
        return self

    @model_validator(mode='after')
    def validate_ping_strategy_requirements(self) -> 'BidirectionalStreamingConfig':
        """
        Ensure ping_interval is meaningful when ping_strategy is not DISABLED.
        """
        if self.ping_strategy != PingStrategy.DISABLED:
            if self.ping_interval > 60.0:
                raise ValueError(
                    f"ping_interval ({self.ping_interval}s) should be <= 60s for {self.ping_strategy.value} strategy"
                )
        return self

    # ------------------------------------------------------------------------
    # Model Configuration
    # ------------------------------------------------------------------------

    model_config = {
        'extra': 'forbid',  # Reject unknown fields (catch typos)
        'frozen': True,     # Immutable (thread-safe)
        'validate_assignment': True,  # Validate on attribute assignment
        'str_strip_whitespace': True,  # Strip strings
        'use_enum_values': False,  # Keep enum objects (not values)
    }

    # ------------------------------------------------------------------------
    # Computed Properties
    # ------------------------------------------------------------------------

    def is_ping_enabled(self) -> bool:
        """Check if ping is enabled."""
        return self.ping_strategy != PingStrategy.DISABLED

    def should_yield_event_loop(self) -> bool:
        """Check if should call await asyncio.sleep(0)."""
        return self.enable_sleep_zero

    def get_effective_ping_timeout(self) -> float:
        """Get ping_timeout with fallback to 6x ping_interval."""
        return self.ping_timeout if self.ping_timeout is not None else self.ping_interval * 6.0


# ============================================================================
# Preset Configurations
# ============================================================================

class ConfigPresets:
    """
    Predefined configurations for common use cases.

    **Available Presets**:
        - PRODUCTION: High-reliability config for production
        - DEVELOPMENT: Relaxed config for development
        - TESTING: Minimal config for unit tests
        - HIGH_THROUGHPUT: Optimized for high message volume
        - LOW_LATENCY: Optimized for responsiveness
    """

    PRODUCTION = BidirectionalStreamingConfig(
        streaming_mode=StreamingMode.ANEXT,
        ping_strategy=PingStrategy.INTERVAL,
        ping_interval=5.0,
        ping_timeout=30.0,
        max_queue_size=1000,
        enable_sleep_zero=True,
        enable_centrifugo=True,
        enable_logging=True,
        max_consecutive_errors=3,
    )
    """Production config: 5s pings, 30s timeout, full logging."""

    DEVELOPMENT = BidirectionalStreamingConfig(
        streaming_mode=StreamingMode.ASYNC_FOR,
        ping_strategy=PingStrategy.ON_IDLE,
        ping_interval=10.0,
        ping_timeout=60.0,
        max_queue_size=100,
        enable_sleep_zero=True,
        enable_centrifugo=False,
        enable_logging=True,
        max_consecutive_errors=10,
    )
    """Development config: Relaxed timeouts, no Centrifugo."""

    TESTING = BidirectionalStreamingConfig(
        streaming_mode=StreamingMode.ASYNC_FOR,
        ping_strategy=PingStrategy.DISABLED,
        ping_interval=1.0,
        max_queue_size=10,
        enable_sleep_zero=False,
        enable_centrifugo=False,
        enable_logging=False,
        max_consecutive_errors=0,
    )
    """Testing config: No pings, minimal queues, no logging."""

    HIGH_THROUGHPUT = BidirectionalStreamingConfig(
        streaming_mode=StreamingMode.ASYNC_FOR,
        ping_strategy=PingStrategy.ON_IDLE,
        ping_interval=30.0,
        ping_timeout=180.0,
        max_queue_size=10000,
        enable_sleep_zero=True,
        enable_centrifugo=True,
        enable_logging=False,  # Reduce overhead
        max_consecutive_errors=10,
    )
    """High throughput: Large queues, infrequent pings, no logging."""

    LOW_LATENCY = BidirectionalStreamingConfig(
        streaming_mode=StreamingMode.ANEXT,
        ping_strategy=PingStrategy.INTERVAL,
        ping_interval=1.0,
        ping_timeout=5.0,
        max_queue_size=100,
        enable_sleep_zero=True,
        enable_centrifugo=True,
        enable_logging=True,
        max_consecutive_errors=3,
    )
    """Low latency: Frequent pings, small queues, immediate responsiveness."""


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Enums
    'StreamingMode',
    'PingStrategy',

    # Models
    'BidirectionalStreamingConfig',

    # Presets
    'ConfigPresets',
]
