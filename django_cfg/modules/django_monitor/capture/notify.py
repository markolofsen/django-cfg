"""
django_monitor.capture.notify — Telegram notifications for monitor events.

Batched alerting: events are accumulated in an in-memory buffer and flushed
as a single Telegram message every N seconds (telegram_batch_interval_sec).

When a new fingerprint appears for the first time, it is flushed immediately
if telegram_alert_on_new=True (default).

All functions fail silently — never break the capture flow.

Requires django_telegram module and CloudflareConfig.telegram_alerts_enabled=True.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from time import time
from typing import Dict

from django_cfg.modules.django_cf import _get_config

logger = logging.getLogger(__name__)

_ALERT_EVENT_TYPES = frozenset({"UNHANDLED_EXCEPTION", "SERVER_ERROR", "RQ_FAILURE", "LOG_ERROR"})
_SLOW_QUERY_ALERT_MS: float = 5000.0


# ─────────────────────────────────────────────────────────────────────────────
# Batch buffer
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class _BatchEntry:
    event_type: str
    message:    str
    api_url:    str
    count:      int = 1
    first_seen: float = field(default_factory=time)


class _AlertBatch:
    """Thread-safe in-memory buffer; flushes on timer or on new fingerprint."""

    def __init__(self) -> None:
        self._lock:    threading.Lock           = threading.Lock()
        self._buffer:  Dict[str, _BatchEntry]   = {}
        self._timer:   threading.Timer | None   = None

    # ── public ────────────────────────────────────────────────────────────────

    def push(
        self,
        fingerprint: str,
        event_type:  str,
        message:     str,
        api_url:     str,
    ) -> None:
        """Add event to buffer; flush immediately if it's a new fingerprint."""
        is_new = False
        with self._lock:
            if fingerprint in self._buffer:
                self._buffer[fingerprint].count += 1
            else:
                self._buffer[fingerprint] = _BatchEntry(
                    event_type=event_type,
                    message=message,
                    api_url=api_url,
                )
                is_new = True
            self._ensure_timer()

        if is_new and _alert_on_new():
            self._flush()

    def flush(self) -> None:
        self._flush()

    # ── internal ──────────────────────────────────────────────────────────────

    def _ensure_timer(self) -> None:
        """Start a flush timer if none is running. Must be called under _lock."""
        if self._timer is None or not self._timer.is_alive():
            interval = _batch_interval()
            self._timer = threading.Timer(interval, self._flush)
            self._timer.daemon = True
            self._timer.start()

    def _flush(self) -> None:
        with self._lock:
            if self._timer and self._timer.is_alive():
                self._timer.cancel()
            self._timer = None
            if not self._buffer:
                return
            snapshot = dict(self._buffer)
            self._buffer.clear()

        _send_batch(snapshot)


_batch = _AlertBatch()


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def notify_server_event(
    event_type:  str,
    message:     str,
    extra:       dict,
    fingerprint: str = "",
    api_url:     str = "",
) -> None:
    """
    Called after a successful D1 push — never raises.
    Accumulates in batch; flushes on new fingerprint or timer.
    """
    try:
        if not _is_alerts_enabled():
            return

        if event_type in _ALERT_EVENT_TYPES:
            _batch.push(
                fingerprint=fingerprint or message[:64],
                event_type=event_type,
                message=message,
                api_url=api_url,
            )
        elif event_type == "SLOW_QUERY":
            elapsed = extra.get("elapsed_ms", 0)
            if elapsed >= _SLOW_QUERY_ALERT_MS:
                _batch.push(
                    fingerprint=fingerprint or f"SLOW_QUERY|{message[:64]}",
                    event_type=event_type,
                    message=f"{message[:200]} ({elapsed:.0f}ms)",
                    api_url=api_url,
                )
    except Exception as exc:
        logger.debug("django_monitor: notify_server_event suppressed — %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# Config helpers
# ─────────────────────────────────────────────────────────────────────────────

def _is_alerts_enabled() -> bool:
    try:
        config = _get_config()
        return bool(config and getattr(config, "telegram_alerts_enabled", False))
    except Exception:
        return False


def _batch_interval() -> int:
    try:
        config = _get_config()
        return int(getattr(config, "telegram_batch_interval_sec", 60))
    except Exception:
        return 60


def _alert_on_new() -> bool:
    try:
        config = _get_config()
        return bool(getattr(config, "telegram_alert_on_new", True))
    except Exception:
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Batch sender
# ─────────────────────────────────────────────────────────────────────────────

_LEVEL_ICON: dict[str, str] = {
    "UNHANDLED_EXCEPTION": "🔴",
    "SERVER_ERROR":        "🔴",
    "RQ_FAILURE":          "🟠",
    "LOG_ERROR":           "🟡",
    "SLOW_QUERY":          "🐢",
}


def _send_batch(snapshot: Dict[str, _BatchEntry]) -> None:
    try:
        from django_cfg.modules.django_telegram import send_error

        total = sum(e.count for e in snapshot.values())
        lines = [f"<b>{total} event(s)</b>"]
        for entry in sorted(snapshot.values(), key=lambda e: -e.count):
            icon = _LEVEL_ICON.get(entry.event_type, "⚪")
            project = f"  <i>{entry.api_url}</i>" if entry.api_url else ""
            lines.append(
                f"{icon} [{entry.event_type}] ×{entry.count} — {entry.message[:120]}{project}"
            )

        send_error("\n".join(lines))
    except Exception as exc:
        logger.debug("django_monitor: _send_batch suppressed — %s", exc)
