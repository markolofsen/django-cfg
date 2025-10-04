"""
Log Formatters

JSON and structured formatters for logging.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """
    JSON structured log formatter.

    Outputs logs in JSON format for easy parsing and analysis.

    Example output:
        {
            "timestamp": "2025-10-04T12:34:56.789Z",
            "level": "INFO",
            "logger": "django_ipc.server",
            "message": "RPC call completed",
            "correlation_id": "abc-123",
            "method": "create_user",
            "duration_ms": 45.2,
            "success": true
        }
    """

    def __init__(
        self,
        include_timestamp: bool = True,
        include_caller: bool = False,
        **kwargs,
    ):
        """
        Initialize JSON formatter.

        Args:
            include_timestamp: Include timestamp in output
            include_caller: Include caller file/line info
        """
        super().__init__(**kwargs)
        self.include_timestamp = include_timestamp
        self.include_caller = include_caller

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON string
        """
        log_data: Dict[str, Any] = {}

        # Timestamp
        if self.include_timestamp:
            log_data["timestamp"] = datetime.utcfromtimestamp(
                record.created
            ).isoformat() + "Z"

        # Basic fields
        log_data["level"] = record.levelname
        log_data["logger"] = record.name
        log_data["message"] = record.getMessage()

        # Caller info (optional - has performance overhead)
        if self.include_caller:
            log_data["file"] = record.pathname
            log_data["line"] = record.lineno
            log_data["function"] = record.funcName

        # Extra fields (correlation_id, method, etc.)
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        if hasattr(record, "method"):
            log_data["method"] = record.method

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        if hasattr(record, "success"):
            log_data["success"] = record.success

        if hasattr(record, "error_code"):
            log_data["error_code"] = record.error_code

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "connection_id"):
            log_data["connection_id"] = record.connection_id

        # Exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Additional custom fields from extra={...}
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "correlation_id", "method",
                "duration_ms", "success", "error_code", "user_id",
                "connection_id",
            ]:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, default=str)


class HumanReadableFormatter(logging.Formatter):
    """
    Human-readable formatter for console output.

    Example output:
        2025-10-04 12:34:56 INFO [abc-123] RPC call: create_user (45.2ms) ✅
    """

    def __init__(self, include_correlation_id: bool = True, **kwargs):
        """
        Initialize human-readable formatter.

        Args:
            include_correlation_id: Include correlation ID in output
        """
        super().__init__(**kwargs)
        self.include_correlation_id = include_correlation_id

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record for human reading.

        Args:
            record: Log record

        Returns:
            Formatted string
        """
        # Timestamp
        timestamp = datetime.utcfromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Level with color (for terminals that support it)
        level = record.levelname
        level_colored = self._colorize_level(level)

        # Correlation ID
        correlation_id = ""
        if self.include_correlation_id and hasattr(record, "correlation_id"):
            correlation_id = f"[{record.correlation_id}] "

        # Message
        message = record.getMessage()

        # Method
        if hasattr(record, "method"):
            message = f"{record.method}: {message}"

        # Duration
        if hasattr(record, "duration_ms"):
            message = f"{message} ({record.duration_ms:.1f}ms)"

        # Success indicator
        if hasattr(record, "success"):
            icon = "✅" if record.success else "❌"
            message = f"{message} {icon}"

        # Build final message
        result = f"{timestamp} {level_colored} {correlation_id}{message}"

        # Exception
        if record.exc_info:
            result += "\n" + self.formatException(record.exc_info)

        return result

    def _colorize_level(self, level: str) -> str:
        """Add color to log level (ANSI codes)."""
        colors = {
            "DEBUG": "\033[36m",     # Cyan
            "INFO": "\033[32m",      # Green
            "WARNING": "\033[33m",   # Yellow
            "ERROR": "\033[31m",     # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        reset = "\033[0m"
        color = colors.get(level, "")
        return f"{color}{level:<8}{reset}"


__all__ = [
    "JSONFormatter",
    "HumanReadableFormatter",
]
