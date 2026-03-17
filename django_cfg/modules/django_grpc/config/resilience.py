"""
django_grpc.config.resilience — Resilience configuration models.

Single source of truth for retry, circuit breaker, and resilience settings.
Pool configuration has been moved to config/pool.py (GrpcPoolConfig).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    import grpc


class RetryConfig(BaseModel):
    """Retry behavior configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True)
    attempts: int = Field(default=5, ge=1, le=20)
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Per-attempt timeout in seconds")
    wait_initial: float = Field(default=0.1, ge=0.01, le=10.0)
    wait_max: float = Field(default=10.0, ge=1.0, le=60.0)
    wait_jitter: float = Field(default=0.1, ge=0.0, le=1.0)
    backoff_multiplier: float = Field(default=2.0, ge=1.0, le=10.0, description="Exponential backoff multiplier")

    @property
    def retryable_status_codes(self) -> set[grpc.StatusCode]:
        """gRPC status codes that should trigger a retry."""
        import grpc
        return {
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.DEADLINE_EXCEEDED,
            grpc.StatusCode.RESOURCE_EXHAUSTED,
            grpc.StatusCode.ABORTED,
        }


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True)
    fail_max: int = Field(default=5, ge=1, le=100)
    reset_timeout: float = Field(default=60.0, ge=1.0, le=3600.0)
    success_threshold: int = Field(default=2, ge=1, le=10)


class ResilienceConfig(BaseModel):
    """Combined resilience configuration (retry + circuit breaker).

    Connection pool configuration is in GrpcPoolConfig (config/pool.py).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    retry: RetryConfig = Field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)


__all__ = [
    "RetryConfig",
    "CircuitBreakerConfig",
    "ResilienceConfig",
]
