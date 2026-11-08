"""
django_monitor.dedupe - write a repeating event once, count the rest.

First occurrence of a fingerprint inside ``WINDOW_SEC`` is logged in full. Repeats
only increment a counter. When the window ends one ``django_cfg.monitor.repeat``
line says how many were folded. This is what a 439 MB ``monitor.log`` day needed:
three fingerprints made almost all of it.

The gate is the Django cache (``cache.add`` is atomic), so with a shared cache
(Redis) the workers agree; with a per-process cache each worker logs the first one
itself. A cache failure fails open: the event is logged in full.

The repeat line is emitted by a daemon timer in the process that logged the first
occurrence. A process that dies inside the window loses that one count line.
"""
from __future__ import annotations

import hashlib
import re
import threading
import time
from typing import Callable, Dict, Optional

WINDOW_SEC = 60
MAX_TRACKED = 5000
_SWEEP_SEC = 5.0

_NOISE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"  # uuid
    r"|\b0x[0-9a-f]+\b|\b[0-9a-f]{12,}\b"  # hex
    r"|\d+",  # numbers
    re.IGNORECASE,
)


def derive_fingerprint(event_type: str, message: str, stack_trace: str = "") -> str:
    """A stable key for an event that came without one: type + normalised message + first stack frame."""
    frame = ""
    for line in (stack_trace or "").splitlines():
        if line.strip():
            frame = line.strip()
            break
    basis = f"{event_type}::{_NOISE.sub('#', message or '')[:300]}::{_NOISE.sub('#', frame)[:200]}"
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


class _Pending:
    __slots__ = ("stream", "record", "expires")

    def __init__(self, stream: str, record: dict, expires: float) -> None:
        self.stream = stream
        self.record = record
        self.expires = expires


_lock = threading.Lock()
_pending: Dict[str, _Pending] = {}
_timer: Optional[threading.Timer] = None
_emit: Optional[Callable[[str, dict], None]] = None


def _cache():
    from django.core.cache import cache

    return cache


def should_log(stream: str, fingerprint: str, record: dict, emit: Callable[[str, dict], None]) -> bool:
    """True when ``record`` is the first of its fingerprint in the window (log it in full).

    ``emit(stream, repeat_record)`` is called later with the folded count.
    """
    global _emit
    if not fingerprint:
        return True
    key = f"{stream}:{fingerprint}"
    try:
        cache = _cache()
        if cache.add(f"cfgmon:seen:{key}", 1, WINDOW_SEC):
            with _lock:
                if len(_pending) >= MAX_TRACKED:
                    return True  # too many distinct keys to follow: log it, count nothing
                _emit = emit
                _pending[key] = _Pending(stream, record, time.time() + WINDOW_SEC + 1)
                _ensure_timer()
            return True
        rep = f"cfgmon:rep:{key}"
        cache.add(rep, 0, WINDOW_SEC * 2)
        cache.incr(rep)
        return False
    except Exception:
        return True


def _ensure_timer() -> None:
    """Under ``_lock``."""
    global _timer
    if _timer is None or not _timer.is_alive():
        _timer = threading.Timer(_SWEEP_SEC, flush_repeats)
        _timer.daemon = True
        _timer.start()


def flush_repeats(force: bool = False) -> int:
    """Emit one repeat line for every expired window with a count. Returns lines emitted."""
    global _timer
    now = time.time()
    due: list[tuple[str, _Pending]] = []
    with _lock:
        _timer = None
        for key, item in list(_pending.items()):
            if force or item.expires <= now:
                due.append((key, _pending.pop(key)))
        if _pending:
            _ensure_timer()
    emitted = 0
    for key, item in due:
        try:
            cache = _cache()
            rep = f"cfgmon:rep:{key}"
            count = int(cache.get(rep, 0) or 0)
            cache.delete(rep)
            if force:
                cache.delete(f"cfgmon:seen:{key}")
            if count > 0 and _emit is not None:
                src = item.record
                _emit("repeat", {
                    "event_type": "MONITOR_REPEAT",
                    "level": "info",
                    "message": f"{count} more of: {str(src.get('message', ''))[:160]}",
                    "fingerprint": src.get("fingerprint", ""),
                    "repeat_of": item.stream,
                    "count": count,
                    "window_s": WINDOW_SEC,
                })
                emitted += 1
        except Exception:
            continue
    return emitted


def _reset() -> None:
    """Forget pending windows (tests)."""
    global _timer
    with _lock:
        _pending.clear()
        if _timer is not None:
            _timer.cancel()
            _timer = None


__all__ = ["WINDOW_SEC", "derive_fingerprint", "flush_repeats", "should_log"]
