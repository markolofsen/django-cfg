"""
Django-CFG gRPC Resilience Layer.

Production-grade retry and circuit breaker patterns for gRPC operations.
Based on cmdop_sdk patterns using stamina and aiobreaker.

Usage:
    from django_cfg.apps.integrations.grpc.resilience import (
        # Retry decorators
        retry_grpc,
        retry_connection,
        retry_streaming,
        with_retry,
        # Circuit breaker
        GRPCCircuitBreaker,
        CircuitOpenError,
        CircuitState,
        # Logging
        get_grpc_logger,
        bind_context,
        clear_context,
        configure_grpc_logging,
    )

    # Apply retry to async function
    @retry_grpc
    async def call_service():
        ...

    # Get or create circuit breaker for target
    breaker = GRPCCircuitBreaker.get_or_create("service-name")
    if breaker.can_execute():
        try:
            result = await call_service()
            breaker.record_success()
        except Exception as e:
            breaker.record_failure(e)
            raise

Created: 2025-12-31
Status: Production
"""

from .retry import (
    retry_grpc,
    retry_connection,
    retry_streaming,
    with_retry,
    is_retryable_error,
    RETRYABLE_STATUS_CODES,
)

from .circuit import (
    GRPCCircuitBreaker,
    CircuitOpenError,
    CircuitState,
)

from .logging import (
    configure_grpc_logging,
    get_grpc_logger,
    bind_context,
    clear_context,
    get_context,
    log_grpc_call,
)

from .config import (
    RetryConfig,
    CircuitBreakerConfig,
    LoggingConfig,
    ResilienceConfig,
)

__all__ = [
    # Retry
    "retry_grpc",
    "retry_connection",
    "retry_streaming",
    "with_retry",
    "is_retryable_error",
    "RETRYABLE_STATUS_CODES",
    # Circuit Breaker
    "GRPCCircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    # Logging
    "configure_grpc_logging",
    "get_grpc_logger",
    "bind_context",
    "clear_context",
    "get_context",
    "log_grpc_call",
    # Config
    "RetryConfig",
    "CircuitBreakerConfig",
    "LoggingConfig",
    "ResilienceConfig",
]
