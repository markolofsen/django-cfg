"""
Resilience configuration models.

Pydantic models for configuring retry, circuit breaker, and logging.

Created: 2025-12-31
"""

from typing import Set, Optional
from pydantic import BaseModel, Field

import grpc


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""

    enabled: bool = Field(default=True, description="Enable retry logic")
    attempts: int = Field(default=5, ge=1, le=20, description="Maximum retry attempts")
    timeout: float = Field(
        default=30.0, ge=1.0, le=300.0, description="Total timeout in seconds"
    )
    wait_initial: float = Field(
        default=0.1, ge=0.01, le=10.0, description="Initial backoff wait in seconds"
    )
    wait_max: float = Field(
        default=10.0, ge=1.0, le=60.0, description="Maximum backoff wait in seconds"
    )
    wait_jitter: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Jitter factor (0.1 = 10%)"
    )

    @property
    def retryable_status_codes(self) -> Set[grpc.StatusCode]:
        """Status codes that should trigger retry."""
        return {
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.DEADLINE_EXCEEDED,
            grpc.StatusCode.RESOURCE_EXHAUSTED,
            grpc.StatusCode.ABORTED,
        }


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker."""

    enabled: bool = Field(default=True, description="Enable circuit breaker")
    fail_max: int = Field(
        default=5, ge=1, le=100, description="Failures before opening circuit"
    )
    reset_timeout: float = Field(
        default=60.0,
        ge=1.0,
        le=3600.0,
        description="Seconds before trying half-open",
    )
    success_threshold: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Successes needed to close from half-open",
    )


class LoggingConfig(BaseModel):
    """Configuration for structured logging."""

    enabled: bool = Field(default=True, description="Enable structured logging")
    json_output: bool = Field(
        default=True, description="Use JSON format (True for production)"
    )
    log_level: str = Field(default="INFO", description="Minimum log level")
    include_request_data: bool = Field(
        default=False, description="Include request data in logs"
    )
    include_response_data: bool = Field(
        default=False, description="Include response data in logs"
    )


class PoolConfig(BaseModel):
    """Configuration for connection pooling."""

    enabled: bool = Field(default=True, description="Enable connection pooling")
    max_size: int = Field(
        default=20, ge=1, le=100, description="Maximum channels in pool"
    )
    idle_timeout: float = Field(
        default=120.0, ge=10.0, le=3600.0, description="Idle timeout in seconds"
    )
    min_idle: int = Field(
        default=2, ge=0, le=10, description="Minimum idle channels per address"
    )
    max_age: float = Field(
        default=3600.0, ge=60.0, le=86400.0, description="Max channel age in seconds"
    )
    cleanup_interval: float = Field(
        default=60.0, ge=10.0, le=600.0, description="Cleanup interval in seconds"
    )


class ResilienceConfig(BaseModel):
    """Combined resilience configuration."""

    retry: RetryConfig = Field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    pool: PoolConfig = Field(default_factory=PoolConfig)

    class Config:
        """Pydantic config."""

        extra = "forbid"


# Default configuration instance
default_config = ResilienceConfig()
