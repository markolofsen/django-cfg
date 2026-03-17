"""
Streaming Logger Utilities for gRPC Services.

Provides reusable logger configuration for gRPC streaming services.
Follows django-cfg logging patterns for consistency.
"""

from __future__ import annotations

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


# ========================================================================
# Module-level debug mode caching (performance optimization)
# ========================================================================

_debug_mode: Optional[bool] = None  # Cached debug mode to avoid repeated config loads


def _get_debug_mode() -> bool:
    """Get debug mode from config (cached at module level)."""
    global _debug_mode

    if _debug_mode is not None:
        return _debug_mode

    try:
        from django_cfg.modules.django_grpc.services.management.config_helper import get_debug_mode
        _debug_mode = get_debug_mode()
    except Exception:
        _debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

    return _debug_mode


class AutoTracebackHandler(logging.Handler):
    """Custom handler that automatically adds exception info to ERROR and CRITICAL logs."""

    def __init__(self, base_handler: logging.Handler):
        super().__init__()
        self.base_handler = base_handler
        self.setLevel(base_handler.level)
        self.setFormatter(base_handler.formatter)

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.ERROR and not record.exc_info:
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                record.exc_info = exc_info
        self.base_handler.emit(record)


def setup_streaming_logger(
    name: str = "grpc_streaming",
    logs_dir: Optional[Path] = None,
    level: Optional[int] = None,
    console_level: Optional[int] = None,
) -> logging.Logger:
    """
    Setup dedicated logger for gRPC streaming with file and console handlers.

    Auto-detects debug mode:
    - debug:      files=DEBUG+, console=DEBUG+
    - production: files=INFO+,  console=WARNING+
    """
    debug = _get_debug_mode()

    if level is None:
        level = logging.DEBUG if debug else logging.INFO
    if console_level is None:
        console_level = logging.DEBUG if debug else logging.WARNING

    streaming_logger = logging.getLogger(name)
    streaming_logger.setLevel(level)

    if streaming_logger.handlers:
        return streaming_logger

    if logs_dir is None:
        logs_dir = Path(os.getcwd()) / 'logs' / 'grpc_streaming'

    logs_dir.mkdir(parents=True, exist_ok=True)

    log_filename = f'streaming_{timezone.now().strftime("%Y%m%d_%H%M%S")}.log'
    log_file_path = logs_dir / log_filename

    base_file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    base_file_handler.setLevel(level)
    base_file_handler.setFormatter(
        logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
    )
    streaming_logger.addHandler(AutoTracebackHandler(base_file_handler))

    base_console_handler = logging.StreamHandler()
    base_console_handler.setLevel(console_level)
    base_console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    streaming_logger.addHandler(AutoTracebackHandler(base_console_handler))

    streaming_logger.propagate = False

    streaming_logger.info("=" * 80)
    streaming_logger.info(f"gRPC Streaming Logger — {name}")
    streaming_logger.info(f"Log file: {log_file_path}")
    streaming_logger.info("=" * 80)

    return streaming_logger


def get_streaming_logger(name: str = "grpc_streaming") -> logging.Logger:
    """Get existing streaming logger or create new one."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_streaming_logger(name)
    return logger


def log_server_start(
    logger: logging.Logger,
    server_type: str = "Server",
    mode: str = "Development",
    hotreload_enabled: bool = False,
    use_rich: bool = True,
    **extra_info: object,
) -> object:
    """Log server startup with timestamp and configuration."""
    from datetime import datetime

    start_time = datetime.now()

    if use_rich:
        console = Console()
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Started at", start_time.strftime('%Y-%m-%d %H:%M:%S'))
        table.add_row("Mode", f"[{'red' if mode == 'Production' else 'green'}]{mode}[/]")
        table.add_row(
            "Hotreload",
            f"[{'yellow' if hotreload_enabled else 'dim'}]{'Enabled' if hotreload_enabled else 'Disabled'}[/]",
        )
        for key, value in extra_info.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        console.print(Panel(
            table,
            title=f"[bold green]{server_type} Starting[/bold green]",
            border_style="green",
            padding=(1, 2),
        ))
    else:
        logger.info(f"{server_type} starting — {mode} — {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        for key, value in extra_info.items():
            logger.info(f"  {key}: {value}")

    return start_time


def log_server_shutdown(
    logger: logging.Logger,
    start_time: object,
    server_type: str = "Server",
    reason: Optional[str] = None,
    use_rich: bool = True,
    **extra_info: object,
) -> None:
    """Log server shutdown with uptime calculation."""
    from datetime import datetime

    end_time = datetime.now()
    uptime = end_time - start_time  # type: ignore[operator]
    uptime_seconds = int(uptime.total_seconds())
    h, rem = divmod(uptime_seconds, 3600)
    m, s = divmod(rem, 60)
    uptime_str = f"{h}h {m}m {s}s"

    if use_rich:
        console = Console()
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        if reason:
            table.add_row("Reason", reason)
        table.add_row("Uptime", f"[bold]{uptime_str}[/bold]")
        table.add_row("Stopped at", end_time.strftime('%Y-%m-%d %H:%M:%S'))
        for key, value in extra_info.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        console.print(Panel(
            table,
            title=f"[bold red]Shutting down {server_type}[/bold red]",
            border_style="red",
            padding=(1, 2),
        ))
    else:
        logger.info(f"{server_type} shutdown — uptime {uptime_str}" + (f" — {reason}" if reason else ""))


__all__ = [
    "setup_streaming_logger",
    "get_streaming_logger",
    "log_server_start",
    "log_server_shutdown",
]
