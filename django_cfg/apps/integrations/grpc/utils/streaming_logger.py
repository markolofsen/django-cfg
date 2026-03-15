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

# Rich for beautiful console output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# ========================================================================
# Module-level debug mode caching (performance optimization)
# ========================================================================

_debug_mode: Optional[bool] = None  # Cached debug mode to avoid repeated config loads


def _get_debug_mode() -> bool:
    """
    Get debug mode from config (cached at module level).

    Loads config only once and caches the result to avoid repeated config loads.
    This is a performance optimization - config loading can be expensive.

    Returns:
        True if debug mode is enabled, False otherwise
    """
    global _debug_mode

    if _debug_mode is not None:
        return _debug_mode

    # Load config once and cache
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        _debug_mode = config.debug if config and hasattr(config, 'debug') else False
    except Exception:
        _debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

    return _debug_mode


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
    level: Optional[int] = None,
    console_level: Optional[int] = None
) -> logging.Logger:
    """
    Setup dedicated logger for gRPC streaming with file and console handlers.

    Follows django-cfg logging pattern:
    - Uses os.getcwd() / 'logs' / 'grpc_streaming' for log directory
    - Time-based log file names (streaming_YYYYMMDD_HHMMSS.log)
    - Auto-detects debug mode for appropriate logging levels
    - In dev/debug: files=DEBUG+, console=DEBUG+
    - In production: files=INFO+, console=WARNING+

    Args:
        name: Logger name (default: "grpc_streaming")
        logs_dir: Directory for log files (default: <cwd>/logs/grpc_streaming)
        level: File logging level (default: auto-detect from debug mode)
        console_level: Console logging level (default: auto-detect from debug mode)

    Returns:
        Configured logger instance

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.utils import setup_streaming_logger

        # Basic usage (auto-detects debug mode)
        logger = setup_streaming_logger()

        # Custom configuration
        logger = setup_streaming_logger(
            name="my_streaming_service",
            logs_dir=Path("/var/log/grpc"),
            level=logging.INFO  # Override auto-detection
        )

        logger.info("Service started")
        logger.debug("Detailed debug info")
        ```

    Features:
        - Automatic log directory creation
        - Time-based log file names
        - No duplicate logs (propagate=False)
        - UTF-8 encoding
        - Debug mode auto-detection (cached for performance)
        - Reusable across all django-cfg gRPC projects
    """
    # Auto-detect debug mode (cached - loaded once)
    debug = _get_debug_mode()

    # Auto-determine logging levels based on debug mode if not explicitly provided
    if level is None:
        # File handlers: DEBUG in dev, INFO in production
        level = logging.DEBUG if debug else logging.INFO

    if console_level is None:
        # Console: DEBUG in dev (full visibility), WARNING in production (reduce noise)
        console_level = logging.DEBUG if debug else logging.WARNING

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

    # Console handler - important messages only (also with auto-traceback)
    base_console_handler = logging.StreamHandler()
    base_console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    base_console_handler.setFormatter(console_formatter)

    # Wrap console handler with auto-traceback too
    console_handler = AutoTracebackHandler(base_console_handler)
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


def log_server_start(
    logger: logging.Logger,
    server_type: str = "Server",
    mode: str = "Development",
    hotreload_enabled: bool = False,
    use_rich: bool = True,
    **extra_info
):
    """
    Log server startup with timestamp and configuration using Rich panels.

    Args:
        logger: Logger instance to use
        server_type: Type of server (e.g., "gRPC Server", "WebSocket Server")
        mode: Running mode (Development/Production)
        hotreload_enabled: Whether hot-reload is enabled
        use_rich: Use Rich for beautiful output (default: True)
        **extra_info: Additional key-value pairs to log

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.utils import log_server_start
        from datetime import datetime

        start_time = log_server_start(
            logger,
            server_type="gRPC Server",
            mode="Development",
            hotreload_enabled=True,
            host="0.0.0.0",
            port=50051
        )
        ```

    Returns:
        datetime object of start time for later use in log_server_shutdown
    """
    from datetime import datetime

    start_time = datetime.now()

    if use_rich:
        # Create Rich table for server info
        console = Console()

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("⏰ Started at", start_time.strftime('%Y-%m-%d %H:%M:%S'))
        table.add_row("Mode", f"[{'red' if mode == 'Production' else 'green'}]{mode}[/]")
        table.add_row("Hotreload", f"[{'yellow' if hotreload_enabled else 'dim'}]{'Enabled ⚡' if hotreload_enabled else 'Disabled'}[/]")

        # Add extra info
        for key, value in extra_info.items():
            key_display = key.replace('_', ' ').title()
            table.add_row(key_display, str(value))

        # Create panel
        panel = Panel(
            table,
            title=f"[bold green]🚀 {server_type} Starting[/bold green]",
            border_style="green",
            padding=(1, 2)
        )

        console.print(panel)

        if hotreload_enabled:
            console.print(
                "[yellow]⚠️  Hotreload active - connections may be dropped on code changes[/yellow]",
                style="bold"
            )
    else:
        # Fallback to simple logging
        logger.info("=" * 80)
        logger.info(f"🚀 {server_type} Starting")
        logger.info(f"   ⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Hotreload: {'Enabled' if hotreload_enabled else 'Disabled'}")

        for key, value in extra_info.items():
            key_display = key.replace('_', ' ').title()
            logger.info(f"   {key_display}: {value}")

        if hotreload_enabled:
            logger.warning(
                "⚠️  Hotreload active - connections may be dropped on code changes"
            )

        logger.info("=" * 80)

    return start_time


def log_server_shutdown(
    logger: logging.Logger,
    start_time,
    server_type: str = "Server",
    reason: str = None,
    use_rich: bool = True,
    **extra_info
):
    """
    Log server shutdown with uptime calculation using Rich panels.

    Args:
        logger: Logger instance to use
        start_time: datetime object from log_server_start()
        server_type: Type of server (e.g., "gRPC Server", "WebSocket Server")
        reason: Shutdown reason (e.g., "Keyboard interrupt", "Hotreload")
        use_rich: Use Rich for beautiful output (default: True)
        **extra_info: Additional key-value pairs to log

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.utils import log_server_shutdown

        log_server_shutdown(
            logger,
            start_time,
            server_type="gRPC Server",
            reason="Hotreload triggered",
            active_connections=5
        )
        ```
    """
    from datetime import datetime

    end_time = datetime.now()
    uptime = end_time - start_time
    uptime_seconds = int(uptime.total_seconds())

    # Format uptime
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    if use_rich:
        # Create Rich table for shutdown info
        console = Console()

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        if reason:
            table.add_row("📋 Reason", reason)

        table.add_row("⏱️  Uptime", f"[bold]{uptime_str}[/bold]")
        table.add_row("🕐 Stopped at", end_time.strftime('%Y-%m-%d %H:%M:%S'))

        # Add extra info
        for key, value in extra_info.items():
            key_display = key.replace('_', ' ').title()
            table.add_row(key_display, str(value))

        # Create panel
        panel = Panel(
            table,
            title=f"[bold red]🧹 Shutting down {server_type}[/bold red]",
            border_style="red",
            padding=(1, 2)
        )

        console.print(panel)
        console.print("[green]✅ Server shutdown complete[/green]", style="bold")
    else:
        # Fallback to simple logging
        logger.info("=" * 80)
        logger.info(f"🧹 Shutting down {server_type}...")

        if reason:
            logger.info(f"   📋 Reason: {reason}")

        logger.info(f"   ⏱️  Uptime: {uptime_str}")
        logger.info(f"   🕐 Stopped at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        for key, value in extra_info.items():
            key_display = key.replace('_', ' ').title()
            logger.info(f"   {key_display}: {value}")

        logger.info("✅ Server shutdown complete")
        logger.info("=" * 80)


__all__ = [
    "setup_streaming_logger",
    "get_streaming_logger",
    "log_server_start",
    "log_server_shutdown",
]
