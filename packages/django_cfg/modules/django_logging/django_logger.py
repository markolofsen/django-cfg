"""
Simple auto-configuring Django Logger for django_cfg.

KISS principle: simple, unified logging configuration.

Features:
- Modular logging with separate files per module
- Automatic log rotation (daily, keeps 30 days)
- INFO+ to files, WARNING+ to console
- Auto-cleanup of old logs
"""

import logging
from logging.handlers import TimedRotatingFileHandler
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
    """Simple auto-configuring logger."""

    _loggers: Dict[str, logging.Logger] = {}
    _configured = False

    @classmethod
    def get_logger(cls, name: str = "django_cfg") -> logging.Logger:
        """Get a configured logger instance."""
        if not cls._configured:
            cls._setup_logging()

        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]

    @classmethod
    def _setup_logging(cls):
        """Setup modular logging configuration with separate files per module."""
        import os
        current_dir = Path(os.getcwd())
        logs_dir = current_dir / 'logs'
        djangocfg_logs_dir = logs_dir / 'djangocfg'

        # Create directories
        logs_dir.mkdir(parents=True, exist_ok=True)
        djangocfg_logs_dir.mkdir(parents=True, exist_ok=True)

        # print(f"[django-cfg] Setting up modular logging:")
        # print(f"  Django logs: {logs_dir / 'django.log'}")
        # print(f"  Django-CFG logs: {djangocfg_logs_dir}/")

        # Get debug mode
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()
            debug = config.debug if config else False
        except Exception:
            debug = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

        # Create handlers
        try:
            # Handler for general Django logs with rotation
            django_log_path = logs_dir / 'django.log'
            django_handler = TimedRotatingFileHandler(
                django_log_path,
                when='midnight',  # Rotate at midnight
                interval=1,  # Every 1 day
                backupCount=30,  # Keep 30 days of logs
                encoding='utf-8',
            )
            django_handler.setLevel(logging.DEBUG if debug else logging.INFO)  # INFO+ in production, DEBUG in dev

            # Console handler - WARNING+ always (less noise)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)

            # Set format for handlers
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s')
            django_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG if debug else logging.INFO)  # INFO+ in production, DEBUG in dev

            # Clear existing handlers
            root_logger.handlers.clear()

            # Add handlers to root logger
            root_logger.addHandler(console_handler)
            root_logger.addHandler(django_handler)  # All logs go to django.log

            # print(f"[django-cfg] Modular logging configured successfully! Debug: {debug}")
            cls._configured = True

        except Exception as e:
            print(f"[django-cfg] ERROR setting up modular logging: {e}")
            # Fallback to console only
            logging.basicConfig(
                level=logging.DEBUG if debug else logging.WARNING,
                format='[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s',
                handlers=[logging.StreamHandler()],
                force=True
            )
            cls._configured = True

    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Create logger with modular file handling for django-cfg loggers."""
        logger = logging.getLogger(name)

        # If this is a django-cfg logger, add a specific file handler
        if name.startswith('django_cfg'):
            try:
                import os
                current_dir = Path(os.getcwd())
                djangocfg_logs_dir = current_dir / 'logs' / 'djangocfg'
                djangocfg_logs_dir.mkdir(parents=True, exist_ok=True)

                # Extract module name from logger name
                # e.g., 'django_cfg.payments.provider' -> 'payments'
                # e.g., 'django_cfg.core' -> 'core'
                # e.g., 'django_cfg' -> 'core'
                parts = name.split('.')
                if len(parts) > 1:
                    module_name = parts[1]  # django_cfg.payments -> payments
                else:
                    module_name = 'core'  # django_cfg -> core

                log_file_path = djangocfg_logs_dir / f'{module_name}.log'

                # Create rotating file handler for this specific module
                file_handler = TimedRotatingFileHandler(
                    log_file_path,
                    when='midnight',  # Rotate at midnight
                    interval=1,  # Every 1 day
                    backupCount=30,  # Keep 30 days of logs
                    encoding='utf-8',
                )

                # Get debug mode
                try:
                    from django_cfg.core.state import get_current_config
                    config = get_current_config()
                    debug = config.debug if config else False
                except Exception:
                    debug = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

                file_handler.setLevel(logging.DEBUG if debug else logging.INFO)  # INFO+ in production, DEBUG in dev

                # Set format
                formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s')
                file_handler.setFormatter(formatter)

                # Add handler to logger
                logger.addHandler(file_handler)
                logger.propagate = True  # Also send to parent (django.log)

                # print(f"[django-cfg] Created modular logger: {name} -> {log_file_path}")

            except Exception as e:
                print(f"[django-cfg] ERROR creating modular logger for {name}: {e}")

        return logger


def clean_old_logs(days: int = 30, logs_dir: Optional[Path] = None) -> Dict[str, int]:
    """
    Clean up log files older than specified days.

    Args:
        days: Number of days to keep (default: 30)
        logs_dir: Optional custom logs directory (default: ./logs)

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
        current_dir = Path(os.getcwd())
        logs_dir = current_dir / 'logs'

    if not logs_dir.exists():
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
def get_logger(name: str = "django_cfg") -> logging.Logger:
    """
    Get a configured logger instance with automatic django-cfg prefix detection.
    
    If called from django-cfg modules, automatically prefixes with 'django_cfg.'
    """
    import inspect

    # Auto-detect if we're being called from django-cfg code
    if not name.startswith('django_cfg'):
        # Get the calling frame to determine if we're in django-cfg code
        frame = inspect.currentframe()
        try:
            # Go up the call stack to find the actual caller
            caller_frame = frame.f_back
            if caller_frame:
                caller_filename = caller_frame.f_code.co_filename

                # Check if caller is from django-cfg modules
                if '/django_cfg/' in caller_filename:
                    # Extract module path from filename
                    # e.g., /path/to/django_cfg/apps/payments/services/providers/registry.py
                    # -> django_cfg.payments.providers

                    parts = caller_filename.split('/django_cfg/')
                    if len(parts) > 1:
                        module_path = parts[1]  # apps/payments/services/providers/registry.py

                        # Convert path to module name
                        if module_path.startswith('apps/'):
                            # apps/payments/services/providers/registry.py -> payments.providers
                            path_parts = module_path.split('/')[1:]  # Remove 'apps'
                            if path_parts:
                                # Remove file extension and 'services' if present
                                clean_parts = []
                                for part in path_parts[:-1]:  # Exclude filename
                                    if part not in ['services', 'management', 'commands']:
                                        clean_parts.append(part)

                                if clean_parts:
                                    auto_name = f"django_cfg.{'.'.join(clean_parts)}"
                                    # print(f"[django-cfg] Auto-detected logger name: {name} -> {auto_name}")
                                    name = auto_name

                        elif module_path.startswith('modules/'):
                            # modules/django_logger.py -> django_cfg.core
                            name = "django_cfg.core"

                        elif module_path.startswith('core/'):
                            # core/config.py -> django_cfg.core
                            name = "django_cfg.core"
        finally:
            del frame

    return DjangoLogger.get_logger(name)


# Export public API
__all__ = ['DjangoLogger', 'get_logger', 'sanitize_extra', 'RESERVED_LOG_ATTRS']
