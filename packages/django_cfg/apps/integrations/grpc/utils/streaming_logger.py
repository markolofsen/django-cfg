"""
Streaming Logger Utilities for gRPC Services.

Provides reusable logger configuration for gRPC streaming services.
Follows django-cfg logging patterns for consistency.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional
from django.utils import timezone


class AutoTracebackHandler(logging.Handler):
    """
    Custom handler that automatically adds exception info to ERROR and CRITICAL logs.

    This ensures full tracebacks are always logged for errors, even if exc_info=True
    is not explicitly specified.
    """

    def __init__(self, base_handler: logging.Handler):
        super().__init__()
        self.base_handler = base_handler
        self.setLevel(base_handler.level)
        self.setFormatter(base_handler.formatter)

    def emit(self, record: logging.LogRecord):
        """Emit log record, automatically adding exc_info for errors."""
        # If ERROR or CRITICAL and no exc_info yet, add current exception if any
        if record.levelno >= logging.ERROR and not record.exc_info:
            # Check if we're in exception context
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                record.exc_info = exc_info

        # Delegate to base handler
        self.base_handler.emit(record)


def setup_streaming_logger(
    name: str = "grpc_streaming",
    logs_dir: Optional[Path] = None,
    level: int = logging.DEBUG,
    console_level: int = logging.INFO
) -> logging.Logger:
    """
    Setup dedicated logger for gRPC streaming with file and console handlers.

    Follows django-cfg logging pattern:
    - Uses os.getcwd() / 'logs' / 'grpc_streaming' for log directory
    - Time-based log file names (streaming_YYYYMMDD_HHMMSS.log)
    - Detailed file logging (DEBUG level by default)
    - Concise console logging (INFO level by default)

    Args:
        name: Logger name (default: "grpc_streaming")
        logs_dir: Directory for log files (default: <cwd>/logs/grpc_streaming)
        level: File logging level (default: DEBUG)
        console_level: Console logging level (default: INFO)

    Returns:
        Configured logger instance

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.utils import setup_streaming_logger

        # Basic usage
        logger = setup_streaming_logger()

        # Custom configuration
        logger = setup_streaming_logger(
            name="my_streaming_service",
            logs_dir=Path("/var/log/grpc"),
            level=logging.INFO
        )

        logger.info("Service started")
        logger.debug("Detailed debug info")
        ```

    Features:
        - Automatic log directory creation
        - Time-based log file names
        - No duplicate logs (propagate=False)
        - UTF-8 encoding
        - Reusable across all django-cfg gRPC projects
    """
    # Create logger
    streaming_logger = logging.getLogger(name)
    streaming_logger.setLevel(level)

    # Avoid duplicate handlers if logger already configured
    if streaming_logger.handlers:
        return streaming_logger

    # Determine logs directory using django-cfg pattern
    if logs_dir is None:
        # Pattern from django_cfg.modules.django_logging:
        # current_dir = Path(os.getcwd())
        # logs_dir = current_dir / 'logs' / 'grpc_streaming'
        current_dir = Path(os.getcwd())
        logs_dir = current_dir / 'logs' / 'grpc_streaming'

    # Create logs directory
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Create log filename with timestamp
    log_filename = f'streaming_{timezone.now().strftime("%Y%m%d_%H%M%S")}.log'
    log_file_path = logs_dir / log_filename

    # File handler - detailed logs with auto-traceback
    base_file_handler = logging.FileHandler(
        log_file_path,
        encoding='utf-8'
    )
    base_file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    base_file_handler.setFormatter(file_formatter)

    # Wrap with auto-traceback handler for automatic exc_info on errors
    file_handler = AutoTracebackHandler(base_file_handler)
    streaming_logger.addHandler(file_handler)

    # Console handler - important messages only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    streaming_logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    streaming_logger.propagate = False

    # Log initialization
    streaming_logger.info("=" * 80)
    streaming_logger.info(f"🌊 {name.title()} Logger Initialized")
    streaming_logger.info(f"📁 Log file: {log_file_path}")
    streaming_logger.info("=" * 80)

    return streaming_logger


def get_streaming_logger(name: str = "grpc_streaming") -> logging.Logger:
    """
    Get existing streaming logger or create new one.

    Args:
        name: Logger name (default: "grpc_streaming")

    Returns:
        Logger instance

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.utils import get_streaming_logger

        logger = get_streaming_logger()
        logger.info("Using existing logger")
        ```
    """
    logger = logging.getLogger(name)

    # If not configured yet, set it up
    if not logger.handlers:
        return setup_streaming_logger(name)

    return logger


__all__ = ["setup_streaming_logger", "get_streaming_logger"]
