"""
RPC Logger with Rotation and Structured Logging

Universal logger for server and clients with:
- Structured JSON logging
- Log rotation (size/time based)
- Separate error logs
- RPC request/response tracking
- Performance metrics
"""

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

from .config import LoggerConfig, LogLevel
from .formatters import JSONFormatter, HumanReadableFormatter


class RPCLogger:
    """
    Universal RPC Logger for server and clients.

    Features:
    - Structured JSON logging to files
    - Human-readable console output
    - Log rotation (size and time based)
    - Separate logs for: app, errors, rpc calls, performance
    - Correlation ID tracking
    - Automatic request/response logging

    Example:
        >>> config = LoggerConfig(
        ...     log_dir="./logs",
        ...     level="INFO",
        ...     log_rpc_calls=True,
        ... )
        >>> logger = RPCLogger(config, name="my_app")
        >>>
        >>> # Simple logging
        >>> logger.info("Server started")
        >>>
        >>> # RPC call logging
        >>> logger.log_rpc_request("create_user", {"username": "john"}, "abc-123")
        >>> logger.log_rpc_response("create_user", {"user_id": "1"}, "abc-123", 45.2, True)
        >>>
        >>> # Error logging
        >>> logger.error("Database error", exc_info=True, correlation_id="abc-123")
    """

    def __init__(
        self,
        config: Optional[LoggerConfig] = None,
        name: str = "django_ipc",
    ):
        """
        Initialize RPC Logger.

        Args:
            config: Logger configuration (uses defaults if None)
            name: Logger name (appears in logs)
        """
        self.config = config or LoggerConfig()
        self.name = name

        # Ensure log directory exists (fallback)
        Path(self.config.log_dir).mkdir(parents=True, exist_ok=True)

        # Create loggers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_log_level(self.config.level))
        self.logger.propagate = False  # Don't propagate to root

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup handlers
        self._setup_handlers()

    def _get_log_level(self, level: LogLevel) -> int:
        """Convert string level to logging constant."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return levels.get(level, logging.INFO)

    def _setup_handlers(self) -> None:
        """Setup log handlers (file and console)."""
        # 1. Main application log (JSON)
        app_handler = self._create_rotating_handler(
            self.config.get_log_file("app"),
            use_json=self.config.use_json,
        )
        self.logger.addHandler(app_handler)

        # 2. Error log (separate file for errors only)
        if self.config.log_errors:
            error_handler = self._create_rotating_handler(
                self.config.get_log_file("error"),
                use_json=self.config.use_json,
                level=logging.ERROR,
            )
            self.logger.addHandler(error_handler)

        # 3. RPC calls log (separate file for RPC tracking)
        if self.config.log_rpc_calls:
            rpc_handler = self._create_rotating_handler(
                self.config.get_log_file("rpc"),
                use_json=True,  # Always JSON for RPC logs
            )
            rpc_handler.addFilter(RPCLogFilter())
            self.logger.addHandler(rpc_handler)

        # 4. Performance log (separate file for metrics)
        if self.config.log_performance:
            perf_handler = self._create_rotating_handler(
                self.config.get_log_file("performance"),
                use_json=True,  # Always JSON for performance logs
            )
            perf_handler.addFilter(PerformanceLogFilter())
            self.logger.addHandler(perf_handler)

        # 5. Console output (human-readable)
        if self.config.console_output:
            console_handler = self._create_console_handler()
            self.logger.addHandler(console_handler)

    def _create_rotating_handler(
        self,
        log_file: Path,
        use_json: bool = True,
        level: int = logging.NOTSET,
    ) -> RotatingFileHandler:
        """
        Create rotating file handler.

        Args:
            log_file: Path to log file
            use_json: Use JSON formatter
            level: Minimum log level

        Returns:
            Configured RotatingFileHandler
        """
        handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=self.config.rotation.max_bytes,
            backupCount=self.config.rotation.backup_count,
            encoding="utf-8",
        )

        handler.setLevel(level)

        # Set formatter
        if use_json:
            formatter = JSONFormatter(
                include_timestamp=self.config.include_timestamp,
                include_caller=self.config.include_caller_info,
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        handler.setFormatter(formatter)

        return handler

    def _create_console_handler(self) -> logging.StreamHandler:
        """
        Create console handler with human-readable format.

        Returns:
            Configured StreamHandler
        """
        handler = logging.StreamHandler(sys.stdout)

        # Console level (uses main level if not specified)
        console_level = self.config.console_level or self.config.level
        handler.setLevel(self._get_log_level(console_level))

        # Human-readable formatter
        formatter = HumanReadableFormatter(
            include_correlation_id=self.config.include_correlation_id,
        )
        handler.setFormatter(formatter)

        return handler

    # ========== Basic Logging Methods ==========

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        # Extract exc_info if present (it's a reserved logging parameter)
        exc_info = kwargs.pop('exc_info', False)
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)

    # ========== RPC-Specific Logging ==========

    def log_rpc_request(
        self,
        method: str,
        params: Dict[str, Any],
        correlation_id: str,
        user_id: Optional[str] = None,
        connection_id: Optional[UUID] = None,
    ) -> None:
        """
        Log RPC request.

        Args:
            method: RPC method name
            params: Request parameters
            correlation_id: Correlation ID for tracking
            user_id: User ID (if available)
            connection_id: Connection ID (if available)

        Example:
            >>> logger.log_rpc_request(
            ...     method="create_user",
            ...     params={"username": "john"},
            ...     correlation_id="abc-123",
            ... )
        """
        if not self.config.log_rpc_calls:
            return

        self.logger.info(
            f"RPC Request: {method}",
            extra={
                "rpc_type": "request",
                "method": method,
                "params": params,
                "correlation_id": correlation_id,
                "user_id": user_id,
                "connection_id": str(connection_id) if connection_id else None,
            },
        )

    def log_rpc_response(
        self,
        method: str,
        result: Any,
        correlation_id: str,
        duration_ms: float,
        success: bool = True,
        error_code: Optional[str] = None,
    ) -> None:
        """
        Log RPC response.

        Args:
            method: RPC method name
            result: Response result
            correlation_id: Correlation ID from request
            duration_ms: Request duration in milliseconds
            success: Whether request succeeded
            error_code: Error code (if failed)

        Example:
            >>> logger.log_rpc_response(
            ...     method="create_user",
            ...     result={"user_id": "1"},
            ...     correlation_id="abc-123",
            ...     duration_ms=45.2,
            ...     success=True,
            ... )
        """
        if not self.config.log_rpc_calls:
            return

        level = logging.INFO if success else logging.ERROR

        self.logger.log(
            level,
            f"RPC Response: {method} ({'success' if success else 'error'})",
            extra={
                "rpc_type": "response",
                "method": method,
                "result": result if success else None,
                "correlation_id": correlation_id,
                "duration_ms": round(duration_ms, 2),
                "success": success,
                "error_code": error_code,
            },
        )

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        **kwargs,
    ) -> None:
        """
        Log performance metric.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            **kwargs: Additional context

        Example:
            >>> logger.log_performance(
            ...     operation="database_query",
            ...     duration_ms=125.5,
            ...     query_type="SELECT",
            ... )
        """
        if not self.config.log_performance:
            return

        self.logger.info(
            f"Performance: {operation}",
            extra={
                "performance": True,
                "operation": operation,
                "duration_ms": round(duration_ms, 2),
                **kwargs,
            },
        )

    def log_connection(
        self,
        event: str,
        connection_id: UUID,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Log connection event.

        Args:
            event: Event type (connect, disconnect, auth, etc.)
            connection_id: Connection ID
            user_id: User ID (if available)
            **kwargs: Additional context

        Example:
            >>> logger.log_connection(
            ...     event="connect",
            ...     connection_id=UUID("..."),
            ...     remote_addr="192.168.1.1",
            ... )
        """
        if not self.config.log_connections:
            return

        self.logger.info(
            f"Connection {event}",
            extra={
                "connection_event": event,
                "connection_id": str(connection_id),
                "user_id": user_id,
                **kwargs,
            },
        )


class RPCLogFilter(logging.Filter):
    """Filter to only pass RPC-related logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Check if record is RPC-related."""
        return hasattr(record, "rpc_type")


class PerformanceLogFilter(logging.Filter):
    """Filter to only pass performance logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Check if record is performance-related."""
        return hasattr(record, "performance")


__all__ = [
    "RPCLogger",
    "RPCLogFilter",
    "PerformanceLogFilter",
]
