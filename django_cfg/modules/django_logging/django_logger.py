"""
Simple auto-configuring Django Logger for django_cfg.

KISS principle: simple, unified logging configuration.

Logging is configured by the generated ``LOGGING`` dict (``config.py``), not at
import time. Default is stdout/stderr; a file is opt-in (``DJANGO_CFG_LOG_DIR``).
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ..base import BaseCfgModule


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


class DjangoLogger(BaseCfgModule):
    """
    Logger factory.

    Importing django-cfg never configures logging: no handlers are added, root
    handlers are not touched, no directories or files are created. Handlers come
    from the ``LOGGING`` dict django-cfg generates (see ``config.py``), which the
    project's own ``LOGGING`` overrides.
    """

    _loggers: Dict[str, logging.Logger] = {}
    _configured = True  # kept for compatibility: there is no lazy setup any more

    @classmethod
    def _get_debug_mode(cls) -> bool:
        """Debug mode from Django settings, then django-cfg config, then env."""
        try:
            from django.conf import settings
            if hasattr(settings, 'DEBUG'):
                return settings.DEBUG
        except Exception:
            pass

        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()
            if config:
                return config.debug if hasattr(config, 'debug') else config.is_development
        except Exception:
            pass

        import os
        if os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes'):
            return True
        return os.getenv('ENV_MODE', '').lower() == 'development'

    @classmethod
    def get_logger(cls, name: str = "django_cfg") -> logging.Logger:
        """Return the standard-library logger for ``name``."""
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        return cls._loggers[name]


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


# Convenience function for quick access
def get_logger(name: str = "") -> logging.Logger:
    """
    Get a configured logger instance with automatic django-cfg prefix detection.

    Automatically detects module path from caller's filename and creates proper logger name.
    If name doesn't start with 'django_cfg', it will be auto-prefixed.

    Examples:
        # Auto-detect from file path
        logger = get_logger()  # -> django_cfg.integrations.rq (from file path)

        # Explicit module name (auto-prefixed)
        logger = get_logger("integrations")  # -> django_cfg.integrations
        logger = get_logger("payments.stripe")  # -> django_cfg.payments.stripe

        # Already prefixed (used as-is)
        logger = get_logger("django_cfg.custom.name")  # -> django_cfg.custom.name
    """
    import inspect
    import os

    # If name is already prefixed with django_cfg, use as-is
    if name and name.startswith('django_cfg'):
        return DjangoLogger.get_logger(name)

    # Auto-detect if we're being called from django-cfg code
    if not name or not name.startswith('django_cfg'):
        frame = inspect.currentframe()
        try:
            # Go up the call stack to find the actual caller
            caller_frame = frame.f_back
            if caller_frame:
                caller_filename = caller_frame.f_code.co_filename

                # Check if caller is from django-cfg modules
                if '/django_cfg/' in caller_filename:
                    # Extract module path from filename
                    parts = caller_filename.split('/django_cfg/')
                    if len(parts) > 1:
                        module_path = parts[1]  # e.g., apps/integrations/rq/tasks/demo_tasks.py

                        # Remove file extension
                        module_path = os.path.splitext(module_path)[0]  # apps/integrations/rq/tasks/demo_tasks

                        # Convert path separators to dots
                        path_parts = module_path.split('/')

                        # Build clean module name based on location
                        clean_parts = []

                        if path_parts[0] == 'apps':
                            # apps/integrations/rq/tasks/demo_tasks -> integrations.rq.tasks
                            # Skip 'apps' and filename, keep directories
                            for part in path_parts[1:-1]:  # Skip 'apps' and filename
                                if part not in ['services', 'management', 'commands', 'views', 'models']:
                                    clean_parts.append(part)

                            # If user provided a name, append it; otherwise use default hierarchy
                            # If user provided a name, append it; otherwise use default hierarchy
                            if name:
                                clean_parts.append(name)

                        elif path_parts[0] == 'modules':
                            # modules/django_logging/logger.py -> core
                            clean_parts = ['core']
                            if name:
                                clean_parts.append(name)

                        elif path_parts[0] == 'core':
                            # core/config.py -> core
                            clean_parts = ['core']
                            if name:
                                clean_parts.append(name)

                        else:
                            # Fallback: use all parts except filename
                            clean_parts = path_parts[:-1]
                            if name:
                                clean_parts.append(name)

                        if clean_parts:
                            auto_name = f"django_cfg.{'.'.join(clean_parts)}"
                            name = auto_name

        finally:
            del frame

    # If we still have a name without django_cfg prefix, add it
    if name and not name.startswith('django_cfg'):
        name = f"django_cfg.{name}"

    # Fallback to default if still no name
    if not name:
        name = "django_cfg"

    return DjangoLogger.get_logger(name)


# Export public API
__all__ = ['DjangoLogger', 'get_logger', 'sanitize_extra', 'RESERVED_LOG_ATTRS']
