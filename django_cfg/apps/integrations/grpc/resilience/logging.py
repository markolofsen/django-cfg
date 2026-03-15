"""
Structured logging using structlog.

Provides JSON-formatted logging with async context propagation.
Based on cmdop_sdk patterns.

Usage:
    from django_cfg.apps.integrations.grpc.resilience import (
        configure_grpc_logging,
        get_grpc_logger,
        bind_context,
        clear_context,
    )

    # Configure at startup
    configure_grpc_logging(json_output=True)

    # Get logger
    logger = get_grpc_logger("MyService")
    logger.info("connected", host="localhost", port=50051)

    # Bind request context
    bind_context(request_id="req-123", user_id="user-456")
    logger.info("processing")  # Includes request_id and user_id
    clear_context()

Created: 2025-12-31
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Conditional import for structlog
try:
    import structlog
    from structlog.typing import FilteringBoundLogger

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None  # type: ignore
    FilteringBoundLogger = Any  # type: ignore

# Context variable for request-scoped data (fallback)
_log_context: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})

# Track if logging is configured
_configured = False


# =============================================================================
# Context Management
# =============================================================================


def bind_context(**kwargs: Any) -> None:
    """
    Bind key-value pairs to the current async context.

    Values will be included in all subsequent log entries
    until clear_context() is called.

    Args:
        **kwargs: Key-value pairs to bind

    Usage:
        bind_context(request_id="req-123", user_id="user-456")
    """
    if STRUCTLOG_AVAILABLE:
        structlog.contextvars.bind_contextvars(**kwargs)
    else:
        current = _log_context.get()
        _log_context.set({**current, **kwargs})


def clear_context() -> None:
    """
    Clear all context bindings.

    Call at the end of request processing.
    """
    if STRUCTLOG_AVAILABLE:
        structlog.contextvars.clear_contextvars()
    else:
        _log_context.set({})


def get_context() -> Dict[str, Any]:
    """
    Get current context bindings.

    Returns:
        Dictionary of current context values
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.contextvars.get_contextvars()
    else:
        return _log_context.get().copy()


# =============================================================================
# Configuration
# =============================================================================


def configure_grpc_logging(
    json_output: bool = True,
    log_level: str = "INFO",
    add_timestamp: bool = True,
) -> None:
    """
    Configure structlog for gRPC services.

    Args:
        json_output: Use JSON format (True for production, False for dev)
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        add_timestamp: Add ISO timestamp to log entries

    Usage:
        # Production
        configure_grpc_logging(json_output=True)

        # Development
        configure_grpc_logging(json_output=False)
    """
    global _configured

    if not STRUCTLOG_AVAILABLE:
        logging.warning("structlog not installed, using standard logging")
        _configure_stdlib_logging(log_level)
        _configured = True
        return

    level = getattr(logging, log_level.upper(), logging.INFO)

    # Build processor chain
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if add_timestamp:
        processors.insert(0, structlog.processors.TimeStamper(fmt="iso"))

    if json_output:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: colored console output
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to use structlog
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Set root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Reduce noise from libraries
    logging.getLogger("grpc").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("aiobreaker").setLevel(logging.WARNING)

    _configured = True


def _configure_stdlib_logging(log_level: str = "INFO") -> None:
    """Configure standard library logging as fallback."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


# =============================================================================
# Logger Factory
# =============================================================================


def get_grpc_logger(name: str) -> Any:
    """
    Get logger for gRPC component.

    Auto-configures if not already configured.

    Args:
        name: Component name (e.g., "client", "interceptor")

    Returns:
        Bound logger instance

    Usage:
        logger = get_grpc_logger("DynamicGRPCClient")
        logger.info("connected", host="localhost")
    """
    global _configured
    if not _configured:
        configure_grpc_logging(json_output=True)

    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(f"grpc.{name}")
    else:
        return logging.getLogger(f"grpc.{name}")


# =============================================================================
# Logging Helpers
# =============================================================================


def log_grpc_call(
    logger: Any,
    service: str,
    method: str,
    success: bool,
    duration_ms: float,
    error: Optional[str] = None,
    status_code: Optional[str] = None,
    **extra: Any,
) -> None:
    """
    Log a gRPC call with standard fields.

    Args:
        logger: Logger instance
        service: Service name
        method: Method name
        success: Whether call succeeded
        duration_ms: Call duration in milliseconds
        error: Error message if failed
        status_code: gRPC status code
        **extra: Additional fields to log

    Usage:
        log_grpc_call(
            logger,
            service="MyService",
            method="GetData",
            success=True,
            duration_ms=45.2,
        )
    """
    event = "grpc_call_success" if success else "grpc_call_error"
    log_method = logger.info if success else logger.error

    log_method(
        event,
        grpc_service=service,
        grpc_method=method,
        duration_ms=round(duration_ms, 2),
        success=success,
        error=error,
        status_code=status_code,
        **extra,
    )


def log_circuit_breaker_event(
    logger: Any,
    target_id: str,
    event_type: str,
    state: str,
    **extra: Any,
) -> None:
    """
    Log circuit breaker events.

    Args:
        logger: Logger instance
        target_id: Target identifier
        event_type: Event type (state_change, blocked, reset)
        state: Current circuit state
        **extra: Additional fields
    """
    logger.warning(
        f"circuit_breaker_{event_type}",
        target_id=target_id,
        circuit_state=state,
        **extra,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "configure_grpc_logging",
    "get_grpc_logger",
    "bind_context",
    "clear_context",
    "get_context",
    "log_grpc_call",
    "log_circuit_breaker_event",
    "STRUCTLOG_AVAILABLE",
]
