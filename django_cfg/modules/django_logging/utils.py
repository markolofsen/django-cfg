"""
Plain helpers around standard-library logging for django_cfg.

There is no logger wrapper: modules use ``logging.getLogger(__name__)``.
Logging is configured by the generated ``LOGGING`` dict (``config.py``), not at
import time. Default is stdout/stderr; a file is opt-in (``DJANGO_CFG_LOG_DIR``).
"""

from pathlib import Path
from typing import Any, Dict, Optional


# Reserved LogRecord attributes that cannot be used in 'extra'
# Source: https://docs.python.org/3/library/logging.html#logrecord-attributes
RESERVED_LOG_ATTRS = {
    'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
    'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
    'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
    'exc_text', 'stack_info', 'asctime', 'taskName'
}


def sanitize_extra(extra: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Sanitize extra dict by prefixing reserved LogRecord attributes.

    Python's logging module reserves certain attribute names in LogRecord.
    Using these names in the 'extra' parameter causes a KeyError.
    This function automatically prefixes conflicting keys with 'ctx_'.

    Args:
        extra: Dictionary of extra logging context

    Returns:
        Sanitized dictionary with no reserved attribute conflicts

    Example:
        >>> sanitize_extra({'module': 'myapp', 'user_id': 123})
        {'ctx_module': 'myapp', 'user_id': 123}
    """
    if not extra:
        return {}

    sanitized = {}
    for key, value in extra.items():
        if key in RESERVED_LOG_ATTRS:
            # Prefix reserved attributes with 'ctx_'
            sanitized[f'ctx_{key}'] = value
        else:
            sanitized[key] = value

    return sanitized


def clean_old_logs(days: int = 30, logs_dir: Optional[Path] = None) -> Dict[str, int]:
    """
    Clean up log files older than specified days.

    Args:
        days: Number of days to keep (default: 30)
        logs_dir: Optional custom logs directory (default: the resolved log dir)

    Returns:
        Dictionary with cleanup statistics

    Example:
        >>> from django_cfg.modules.django_logging import clean_old_logs
        >>> stats = clean_old_logs(days=7)  # Keep only last 7 days
        >>> print(f"Deleted {stats['deleted']} files, freed {stats['bytes']} bytes")
    """
    import os
    from datetime import datetime, timedelta

    if logs_dir is None:
        from django_cfg.core.utils.runtime_paths import resolve_log_dir
        logs_dir = resolve_log_dir()

    if logs_dir is None or not logs_dir.exists():
        return {'deleted': 0, 'bytes': 0, 'error': 'Logs directory not found'}

    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    deleted_bytes = 0

    # Recursively find all .log files (including rotated ones like .log.2024-11-01)
    for log_file in logs_dir.rglob('*.log*'):
        if log_file.is_file():
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    file_size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_count += 1
                    deleted_bytes += file_size
            except Exception as e:
                print(f"[django-cfg] Error deleting {log_file}: {e}")

    return {
        'deleted': deleted_count,
        'bytes': deleted_bytes,
        'human_readable': f"{deleted_bytes / 1024 / 1024:.2f} MB" if deleted_bytes > 0 else "0 MB",
    }


__all__ = ["sanitize_extra", "clean_old_logs", "RESERVED_LOG_ATTRS"]
