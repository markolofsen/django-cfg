"""
django_grpc.config.streaming — Bidirectional streaming configuration.

connection_timeout was removed (Bug #1): asyncio.wait_for() on request_iterator
corrupts grpcio's internal stream state machine. Use ping_strategy + ping_interval instead.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StreamingMode(str, Enum):
    ASYNC_FOR = "async_for"
    ANEXT = "anext"


class PingStrategy(str, Enum):
    INTERVAL = "interval"
    ON_IDLE = "on_idle"
    DISABLED = "disabled"


class BidirectionalStreamingConfig(BaseModel):
    """
    Configuration for bidirectional gRPC streaming.

    connection_timeout was removed — see Bug #1. A before-validator rejects it with a helpful error.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    streaming_mode: StreamingMode = Field(default=StreamingMode.ANEXT)
    ping_strategy: PingStrategy = Field(default=PingStrategy.INTERVAL)
    ping_interval: float = Field(default=5.0, gt=0, le=300)
    ping_timeout: Optional[float] = Field(default=None)

    max_queue_size: int = Field(default=1000, gt=0, le=100_000)
    enable_sleep_zero: bool = Field(
        default=True,
        description="await asyncio.sleep(0) in input loop — prevents output loop starvation",
    )

    enable_logging: bool = Field(default=True)
    enable_centrifugo: bool = Field(default=True)
    centrifugo_channel_prefix: str = Field(default="grpc")

    @model_validator(mode="before")
    @classmethod
    def _reject_connection_timeout(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("connection_timeout") is not None:
            raise ValueError(
                "connection_timeout is removed — it caused Bug #1 (StopAsyncIteration). "
                "Use ping_strategy + ping_interval for liveness detection."
            )
        return data

    @model_validator(mode="after")
    def set_ping_timeout(self) -> Self:
        if self.ping_timeout is None:
            object.__setattr__(self, "ping_timeout", self.ping_interval * 6)
        return self


class ConfigPresets:
    """Pre-built streaming configs for common scenarios."""

    PRODUCTION = BidirectionalStreamingConfig(ping_interval=5.0)
    DEVELOPMENT = BidirectionalStreamingConfig(
        ping_interval=10.0,
        enable_centrifugo=False,
    )
    TESTING = BidirectionalStreamingConfig(
        ping_strategy=PingStrategy.DISABLED,
        enable_centrifugo=False,
        enable_logging=False,
    )
    HIGH_THROUGHPUT = BidirectionalStreamingConfig(
        ping_interval=30.0,
        max_queue_size=10_000,
    )


__all__ = [
    "BidirectionalStreamingConfig",
    "StreamingMode",
    "PingStrategy",
    "ConfigPresets",
]
