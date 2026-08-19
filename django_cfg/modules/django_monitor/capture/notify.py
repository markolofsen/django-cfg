"""
django_monitor.capture.notify — Telegram notifications for monitor events.

Batched alerting: events are accumulated in an in-memory buffer and flushed
as a single Telegram message every 60 seconds. A new fingerprint (first
occurrence) is flushed immediately.

All functions fail silently — never break the capture flow.

Alerts are enabled automatically when TelegramConfig is set on DjangoConfig —
no separate switch.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from time import time
from typing import Dict

logger = logging.getLogger(__name__)

_ALERT_EVENT_TYPES = frozenset({"UNHANDLED_EXCEPTION", "SERVER_ERROR", "RQ_FAILURE", "LOG_ERROR", "FRONTEND_ERROR"})
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
    # The buffer's dict key is a fingerprint OR a `message[:64]` fallback
    # (see notify_server_event) and the two are indistinguishable once used
    # as a key. This field carries ONLY a real, upstream-computed fingerprint
    # — blank when the caller supplied none — because the alert prints it as
    # a stable join key and a truncated message is not one.
    fingerprint: str = ""


class _AlertBatch:
    """Thread-safe in-memory buffer; flushes on timer or on new fingerprint.

    "New" is judged against fingerprints alerted within the last
    ``NEW_FINGERPRINT_TTL_SEC`` — NOT against the current buffer (which is
    cleared on every flush; judging by the buffer would make every repeat
    of the same error flush immediately and defeat batching entirely).
    """

    NEW_FINGERPRINT_TTL_SEC = 600  # re-alert the same fingerprint immediately at most every 10 min

    def __init__(self) -> None:
        self._lock:    threading.Lock           = threading.Lock()
        self._buffer:  Dict[str, _BatchEntry]   = {}
        self._recent:  Dict[str, float]         = {}
        self._timer:   threading.Timer | None   = None

    # ── public ────────────────────────────────────────────────────────────────

    def push(
        self,
        fingerprint: str,
        event_type:  str,
        message:     str,
        api_url:     str,
        real_fingerprint: str = "",
    ) -> None:
        """Add event to buffer; flush immediately if the fingerprint is new.

        ``fingerprint`` is the dedup KEY (possibly a message-derived fallback);
        ``real_fingerprint`` is the upstream-computed one, or blank. Keeping
        them separate is what lets the alert print a join key without ever
        printing a truncated message dressed up as one.
        """
        now = time()
        with self._lock:
            if fingerprint in self._buffer:
                self._buffer[fingerprint].count += 1
            else:
                self._buffer[fingerprint] = _BatchEntry(
                    event_type=event_type,
                    message=message,
                    api_url=api_url,
                    fingerprint=real_fingerprint,
                )
            is_new = now - self._recent.get(fingerprint, 0.0) > self.NEW_FINGERPRINT_TTL_SEC
            if is_new:
                self._recent[fingerprint] = now
                if len(self._recent) > 500:
                    cutoff = now - self.NEW_FINGERPRINT_TTL_SEC
                    self._recent = {k: v for k, v in self._recent.items() if v > cutoff}
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
    Called from capture after the event is stored — never raises.
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
                real_fingerprint=fingerprint,
            )
        elif event_type == "SLOW_QUERY":
            elapsed = extra.get("elapsed_ms", 0)
            if elapsed >= _SLOW_QUERY_ALERT_MS:
                _batch.push(
                    fingerprint=fingerprint or f"SLOW_QUERY|{message[:64]}",
                    event_type=event_type,
                    message=f"{message[:200]} ({elapsed:.0f}ms)",
                    api_url=api_url,
                    real_fingerprint=fingerprint,
                )
    except Exception as exc:
        logger.debug("django_monitor: notify_server_event suppressed — %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# Config helpers
# ─────────────────────────────────────────────────────────────────────────────

def _is_alerts_enabled() -> bool:
    """Alerts are on exactly when Telegram is configured."""
    try:
        from django_cfg.core.state.registry import get_current_config
        cfg = get_current_config()
        return bool(cfg and getattr(cfg, "telegram", None))
    except Exception:
        return False


def _batch_interval() -> int:
    return 60


def _alert_on_new() -> bool:
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Batch sender
# ─────────────────────────────────────────────────────────────────────────────

_LEVEL_ICON: dict[str, str] = {
    "UNHANDLED_EXCEPTION": "🔴",
    "SERVER_ERROR":        "🔴",
    "RQ_FAILURE":          "🟠",
    "LOG_ERROR":           "🟡",
    "FRONTEND_ERROR":      "🌐",
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
            # The fingerprint is computed at capture time and was, until now,
            # used as a buffer key and then discarded — so an operator reading
            # a repeat alert had no stable key to join two occurrences by, and
            # no way to correlate an alert with anything else keyed on the same
            # value. Printing it costs nothing — no store, no retention, and
            # nothing readable: every producer hashes with sha256 and keeps 16
            # hex chars, over an exception signature (request.py:57, rq.py:75,
            # log_handler.py:58) or over SQL with the literals already stripped
            # (slow_query.py:40,81). It is the whole reason this is worth a
            # line: server events are log-only, so the alert is the only place
            # the key can surface at all.
            #
            # Omitted rather than faked when blank. Only the frontend ingest
            # path can produce a blank one (the four server capture sites all
            # stamp unconditionally), and there the honest output is no key —
            # printing the fallback would advertise `message[:64]` as a stable
            # identifier when it changes with every distinct message.
            fp = f"  <code>{entry.fingerprint}</code>" if entry.fingerprint else ""
            lines.append(
                f"{icon} [{entry.event_type}] ×{entry.count} — {entry.message[:120]}{fp}{project}"
            )

        send_error("\n".join(lines))
    except Exception as exc:
        logger.debug("django_monitor: _send_batch suppressed — %s", exc)
