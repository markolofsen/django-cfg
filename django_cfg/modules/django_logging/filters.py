"""Filters on the one console handler: access-log junk and correlation context."""
from __future__ import annotations

import logging
import re
from typing import Iterable, Optional

from .context import current_ids

ACCESS_LOGGERS = ("uvicorn.access", "gunicorn.access", "django.server")

#: Health-check and static paths: successful hits are dropped from access logs.
DEFAULT_IGNORE_PATHS = ("/healthz", "/health", "/readyz", "/ready", "/live", "/ping", "/static/", "/favicon.ico")

_REQ = re.compile(r'"[A-Z]+ (\S+) HTTP/[\d.]+"(?: (\d{3}))?')


def _path_matches(path: str, prefix: str) -> bool:
    path = path.split("?", 1)[0]
    if prefix.endswith("/"):
        return path.startswith(prefix)
    return path == prefix or path.startswith(prefix + "/")


class AccessJunkFilter(logging.Filter):
    """Drop access-log lines for health/static paths that succeeded (status < 400)."""

    def __init__(self, paths: Optional[Iterable[str]] = None):
        super().__init__()
        self.paths = tuple(DEFAULT_IGNORE_PATHS if paths is None else paths)

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name not in ACCESS_LOGGERS or not self.paths:
            return True
        path: Optional[str] = None
        status: Optional[int] = None
        args = record.args
        if isinstance(args, tuple) and len(args) == 5:  # uvicorn.access: client, method, path, http, status
            path = str(args[2])
            try:
                status = int(args[4])
            except (TypeError, ValueError):
                status = None
        else:
            m = _REQ.search(record.getMessage())
            if m:
                path = m.group(1)
                status = int(m.group(2)) if m.group(2) else None
        if path is None or (status is not None and status >= 400):
            return True
        return not any(_path_matches(path, p) for p in self.paths)


class ContextFilter(logging.Filter):
    """Write ``request_id`` / ``trace_id`` / ``span_id`` / ``job_id`` onto the record when known."""

    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in current_ids().items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True
