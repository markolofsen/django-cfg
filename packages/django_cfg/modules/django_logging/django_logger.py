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
    _debug_mode: Optional[bool] = None  # Cached debug mode to avoid repeated config loads

    @classmethod
    def _get_debug_mode(cls) -> bool:
        """
        Get debug mode from config dynamically (no caching).

        Loads config each time to ensure we get the correct debug state.
        This is necessary because config may not be ready when logger is first initialized.

        Returns:
            True if debug mode is enabled (config.debug or config.is_development), False otherwise
        """
        # Try Django settings first (most reliable)
        try:
            from django.conf import settings
            if hasattr(settings, 'DEBUG'):
                return settings.DEBUG
        except Exception:
            pass

        # Try config second
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()

            # Return debug if available, fallback to is_development
            if config:
                return config.debug if hasattr(config, 'debug') else config.is_development
        except Exception:
            pass

        # Fallback to environment variables if nothing else works
        import os
        debug_env = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
        if debug_env:
            return True
        env_mode = os.getenv('ENV_MODE', '').lower()
        return env_mode == 'development'

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

        # Get debug mode (cached - loaded once)
        debug = cls._get_debug_mode()

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
            # File handlers ALWAYS capture DEBUG in dev mode (for complete debugging history)
            # In production, still use INFO+ to save disk space
            django_handler.setLevel(logging.DEBUG if debug else logging.INFO)

            # /tmp handler - always enabled for easy `tail -f /tmp/djangocfg/debug.log`
            # Set DJANGO_LOG_TO_TMP=false to disable
            import os
            tmp_handler = None
            if os.getenv('DJANGO_LOG_TO_TMP', 'true').lower() not in ('false', '0', 'no'):
                try:
                    # Use /tmp/djangocfg/ directory
                    tmp_log_dir = Path('/tmp') / 'djangocfg'
                    tmp_log_dir.mkdir(parents=True, exist_ok=True)
                    tmp_log_path = tmp_log_dir / 'debug.log'
                    tmp_handler = logging.FileHandler(tmp_log_path, mode='a', encoding='utf-8')
                    tmp_handler.setLevel(logging.DEBUG)  # Always capture everything
                except Exception as e:
                    print(f"[django-cfg] Failed to create /tmp/djangocfg/debug.log: {e}")

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)

            # Set format for all handlers
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s')
            django_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            if tmp_handler:
                tmp_handler.setFormatter(formatter)

            # Configure root logger - ALWAYS DEBUG to let handlers filter
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)  # CRITICAL: Always DEBUG, handlers filter

            # Clear existing handlers
            root_logger.handlers.clear()

            # Add handlers to root logger
            root_logger.addHandler(console_handler)
            root_logger.addHandler(django_handler)
            if tmp_handler:
                root_logger.addHandler(tmp_handler)
                # Test log to verify handler works
                root_logger.info("[django-cfg] Logging initialized")

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
        """
        Create logger with modular file handling for django-cfg loggers.

        In dev/debug mode, loggers are set to DEBUG level to ensure all log messages
        reach file handlers. Handlers still filter console output (WARNING+), but files
        get everything (DEBUG+).
        """
        logger = logging.getLogger(name)

        # Get debug mode (cached - loaded once)
        debug = cls._get_debug_mode()

        # CRITICAL: ALWAYS set DEBUG level on django_cfg loggers
        # This ensures all messages (DEBUG/INFO/WARNING/ERROR) can reach handlers
        # Handlers will do the filtering, not the logger itself
        if name.startswith('django_cfg'):
            logger.setLevel(logging.DEBUG)

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

                # Get debug mode (cached - loaded once)
                debug = cls._get_debug_mode()

                # Module file handlers ALWAYS capture DEBUG in dev mode
                # This ensures complete log history for debugging, independent of logger level
                file_handler.setLevel(logging.DEBUG if debug else logging.INFO)

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
