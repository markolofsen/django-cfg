"""
Collapse repeated log records: the first passes at once, repeats are counted.

Key (a repeat means the SAME line, never merely the same call site):

- ``(logger, level, pathname, lineno, formatted message)``: the arguments are part of the
  key, so three ``Not Found: %s`` warnings for three paths are three lines, and a rate-limit
  or auth-failure warning keeps the address it is about. Only an identical line repeats;
- a record with ``exc_info``: ``(logger, level, message template, exception type, INNERMOST
  traceback frame)``, the place that raised, not the ``try`` that caught it. Two different
  errors caught by one handler are two keys, so a NEW traceback always prints;
- ``extra={"collapse_key": "..."}`` at a call site replaces the message part of the key: the
  opt-in for a line whose arguments are noise (``"retry %s"`` with a counter).

Rules: the first record of a key always passes; repeats inside ``window_seconds`` are
dropped and counted; the count leaves as ``... (repeated N times in 60s, pid P)`` when
the key's next record arrives after the window, when any later record sweeps a key that
went quiet, or at shutdown. ERROR and above are never collapsed, nor is a record with
``extra={"no_collapse": True}``, nor a monitor event or an access-log line. At most
``max_keys`` keys are tracked (LRU; an evicted key's pending count is emitted first).
Any internal failure lets the record pass.

State is per process: N workers can each print the first line. Not shared through Redis.
"""
from __future__ import annotations

import logging
import os
import threading
import time
import traceback
from collections import OrderedDict
from typing import Callable, List, Optional

_NO_COLLAPSE_NAMES = ("uvicorn.access", "gunicorn.access", "django.server", "django_cfg.monitor")
_SWEEP_SECONDS = 5.0


def _exempt(record: logging.LogRecord) -> bool:
    if record.levelno >= logging.ERROR or getattr(record, "no_collapse", False):
        return True
    if getattr(record, "monitor_event", None) is not None:
        return True
    name = record.name
    return any(name == n or name.startswith(n + ".") for n in _NO_COLLAPSE_NAMES)


def _message(record: logging.LogRecord) -> str:
    try:
        return record.getMessage()
    except Exception:
        return str(record.msg)


def record_key(record: logging.LogRecord) -> tuple:
    explicit = getattr(record, "collapse_key", None)
    if record.exc_info and record.exc_info[0] is not None:
        exc_type, _, tb = record.exc_info
        frame = ""
        if tb is not None:
            try:
                fs = traceback.extract_tb(tb)
                if fs:
                    inner = fs[-1]  # where it was raised, not where it was caught
                    frame = f"{inner.filename}:{inner.lineno}:{inner.name}"
            except Exception:
                frame = ""
        return (record.name, record.levelno, "exc", str(explicit) if explicit else str(record.msg), exc_type.__name__, frame)
    return (record.name, record.levelno, record.pathname, record.lineno, str(explicit) if explicit else _message(record))


class _Entry:
    __slots__ = ("first", "suppressed", "sample")

    def __init__(self, first: float, sample: logging.LogRecord) -> None:
        self.first = first
        self.suppressed = 0
        self.sample = sample


class Collapser:
    """The collapse state machine. ``process(record)`` returns the records to emit now."""

    def __init__(
        self,
        window_seconds: float = 60.0,
        max_keys: int = 1000,
        clock: Callable[[], float] = time.monotonic,
        pid: Optional[int] = None,
    ) -> None:
        self.window = float(window_seconds)
        self.max_keys = max(1, int(max_keys))
        self._clock = clock
        self._pid = os.getpid() if pid is None else pid
        self._entries: "OrderedDict[tuple, _Entry]" = OrderedDict()
        self._lock = threading.Lock()
        self._last_sweep = clock()
        self.suppressed_total = 0
        self.keys_evicted = 0

    def _summary(self, entry: _Entry) -> logging.LogRecord:
        s = entry.sample
        window = int(self.window) if self.window == int(self.window) else self.window
        text = f"{s.getMessage()} (repeated {entry.suppressed} times in {window}s, pid {self._pid})"
        return logging.makeLogRecord(
            {
                "name": s.name, "levelno": s.levelno, "levelname": s.levelname,
                "pathname": s.pathname, "filename": s.filename, "module": s.module,
                "lineno": s.lineno, "funcName": s.funcName, "msg": text, "args": None,
                "collapsed_count": entry.suppressed,
            }
        )

    def process(self, record: logging.LogRecord) -> List[logging.LogRecord]:
        if _exempt(record):
            return [record]
        try:
            return self._process(record)
        except Exception:  # fail open
            return [record]

    def _process(self, record: logging.LogRecord) -> List[logging.LogRecord]:
        now = self._clock()
        out: List[logging.LogRecord] = []
        key = record_key(record)
        with self._lock:
            if now - self._last_sweep >= _SWEEP_SECONDS:
                self._last_sweep = now
                for k in [k for k, e in self._entries.items() if k != key and now - e.first >= self.window]:
                    e = self._entries.pop(k)
                    if e.suppressed:
                        out.append(self._summary(e))
            entry = self._entries.get(key)
            if entry is not None and now - entry.first < self.window:
                entry.suppressed += 1
                self.suppressed_total += 1
                self._entries.move_to_end(key)
                return out
            if entry is not None:
                if entry.suppressed:
                    out.append(self._summary(entry))
                del self._entries[key]
            self._entries[key] = _Entry(now, _sample(record))
            while len(self._entries) > self.max_keys:
                _, old = self._entries.popitem(last=False)
                self.keys_evicted += 1
                if old.suppressed:
                    out.append(self._summary(old))
        out.append(record)
        return out

    def drain(self) -> List[logging.LogRecord]:
        """Summaries of every key with a pending count (shutdown)."""
        with self._lock:
            out = [self._summary(e) for e in self._entries.values() if e.suppressed]
            self._entries.clear()
        return out

    def stats(self) -> dict:
        return {"suppressed_total": self.suppressed_total, "keys_evicted": self.keys_evicted, "keys": len(self._entries)}


def _sample(record: logging.LogRecord) -> logging.LogRecord:
    """A light copy for the summary (no exc_info held, message formatted once)."""
    try:
        msg = record.getMessage()
    except Exception:
        msg = str(record.msg)
    return logging.makeLogRecord(
        {
            "name": record.name, "levelno": record.levelno, "levelname": record.levelname,
            "pathname": record.pathname, "filename": record.filename, "module": record.module,
            "lineno": record.lineno, "funcName": record.funcName, "msg": msg, "args": None,
        }
    )


class CollapsingStreamHandler(logging.StreamHandler):
    """The one console handler: handler filters, then collapse, then emit."""

    def __init__(self, stream=None, window_seconds: float = 60.0, max_keys: int = 1000, collapse: bool = True):
        super().__init__(stream)
        self.collapser: Optional[Collapser] = Collapser(window_seconds, max_keys) if collapse else None

    def handle(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        if self.collapser is None:
            return super().handle(record)
        if not self.filter(record):
            return False
        out = self.collapser.process(record)
        if not out:
            return False
        self.acquire()
        try:
            for r in out:
                self.emit(r)
        finally:
            self.release()
        return record in out

    def close(self) -> None:
        if self.collapser is not None:
            try:
                self.acquire()
                try:
                    for r in self.collapser.drain():
                        self.emit(r)
                finally:
                    self.release()
            except Exception:
                pass
        super().close()


def collapse_stats() -> dict:
    """Counters of the root collapsing handler (``suppressed_total``, ``keys_evicted``, ``keys``)."""
    for h in logging.getLogger().handlers:
        c = getattr(h, "collapser", None)
        if c is not None:
            return c.stats()
    return {"suppressed_total": 0, "keys_evicted": 0, "keys": 0}
