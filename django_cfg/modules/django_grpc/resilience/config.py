"""
django_grpc.resilience.config — Resilience configuration models.

RetryConfig, CircuitBreakerConfig, and ResilienceConfig are imported from
the canonical location (config/resilience.py) to avoid duplication.

LoggingConfig is defined here as it is unique to the resilience package
and has no counterpart in the main config hierarchy.
PoolConfig is imported from config/pool.py (the single canonical definition).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from django_cfg.modules.django_grpc.config.pool import GrpcPoolConfig
from django_cfg.modules.django_grpc.config.resilience import (
    CircuitBreakerConfig,
    ResilienceConfig,
    RetryConfig,
)

# PoolConfig alias so existing resilience/ code doesn't break
PoolConfig = GrpcPoolConfig


class LoggingConfig(BaseModel):
    """Configuration for structured logging within the resilience package."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True)
    json_output: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    include_request_data: bool = Field(default=False)
    include_response_data: bool = Field(default=False)


# Default configuration instance (used by resilience package internals)
default_config = ResilienceConfig()

__all__ = [
    "RetryConfig",
    "CircuitBreakerConfig",
    "LoggingConfig",
    "PoolConfig",
    "GrpcPoolConfig",
    "ResilienceConfig",
    "default_config",
]
