"""
Django Logging module for django_cfg.

There is no logger wrapper: use ``logging.getLogger(__name__)``. This module
provides the generated ``LOGGING`` dict (``config.build_logging_config``).
Records go to stdout/stderr; a file is opt-in via DJANGO_CFG_LOG_DIR
(WatchedFileHandler, external logrotate). Importing creates no files or
directories. Error-level records are additionally captured by django_monitor
(JSONL + Telegram alerts).
"""

from .utils import RESERVED_LOG_ATTRS, clean_old_logs, sanitize_extra

__all__ = ["sanitize_extra", "clean_old_logs", "RESERVED_LOG_ATTRS"]
