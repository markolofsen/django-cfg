"""
RPC Logger Module

Universal logging solution for django-ipc server and clients.

Features:
- Structured JSON logging
- Log rotation (size/time based)
- Separate logs for: app, errors, rpc, performance
- Correlation ID tracking
- Automatic RPC request/response logging
- Performance metrics

Example:
    >>> from django_ipc.logger import RPCLogger, LoggerConfig
    >>>
    >>> # Configure logger
    >>> config = LoggerConfig(
    ...     log_dir="./logs",
    ...     level="INFO",
    ...     log_rpc_calls=True,
    ... )
    >>> logger = RPCLogger(config, name="my_rpc_server")
    >>>
    >>> # Simple logging
    >>> logger.info("Server started")
    >>>
    >>> # RPC logging
    >>> logger.log_rpc_request("create_user", {...}, "abc-123")
    >>> logger.log_rpc_response("create_user", {...}, "abc-123", 45.2, True)
    >>>
    >>> # With middleware
    >>> from django_ipc.logger import auto_log_rpc
    >>>
    >>> @auto_log_rpc(logger)
    >>> @router.register("create_user")
    >>> async def create_user(conn, params):
    ...     return UserResult(...)
"""

from .config import (
    LoggerConfig,
    LogRotationConfig,
    LogLevel,
)

from .formatters import (
    JSONFormatter,
    HumanReadableFormatter,
)

from .logger import (
    RPCLogger,
    RPCLogFilter,
    PerformanceLogFilter,
)

from .middleware import (
    LoggingMiddleware,
    auto_log_rpc,
)

__all__ = [
    # Configuration
    "LoggerConfig",
    "LogRotationConfig",
    "LogLevel",
    # Formatters
    "JSONFormatter",
    "HumanReadableFormatter",
    # Logger
    "RPCLogger",
    "RPCLogFilter",
    "PerformanceLogFilter",
    # Middleware
    "LoggingMiddleware",
    "auto_log_rpc",
]
