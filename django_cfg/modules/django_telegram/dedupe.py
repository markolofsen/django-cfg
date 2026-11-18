"""
django_telegram.dedupe - send the same text to the same chat once per window.

The gate sits in ``DjangoTelegram.send_message``, the one point every path ends in
(shortcuts, ``send_telegram_message``, ``send_admin_notification``, the monitor,
RQ alerting, accounts, Notion). The first message of a key passes at once; repeats
inside the window are counted and dropped; when the window ends one summary line
("Repeated N times ...") is sent, so a count is never lost.

State is the Django cache (``cache.add`` is the atomic first gate, ``incr`` the
counter): with a shared cache (Redis) every process and worker agrees; with a
per-process cache each process sends its own first message. Any cache error fails
open (the message is sent).

The summary is sent by a daemon timer in the process that sent the first message.
If that process dies inside the window, the next identical message after the window
carries the count instead ("repeated N times before"). Only if neither happens is
a count lost.

Photos and documents are not deduped (no text). The OTP notification opts out with
``dedupe=False``; so can any caller.
"""
from __future__ import annotations

import hashlib
import html
import logging
import re
import threading
import time
from typing import Callable, Dict, Optional, Tuple

logger = logging.getLogger("django_cfg.telegram.dedupe")

DEFAULT_WINDOW_SEC = 60
MAX_TRACKED = 5000
_SWEEP_SEC = 5.0
HEAD_CHARS = 160

_TAGS = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")
# What is folded is only what changes with every occurrence of the SAME event: a
# timestamp, a clock time, a UUID, a long hex string (a trace or request id). Every
# other number stays in the key on purpose: an amount, an order or user id, a count,
# an HTTP status. "Payment 12000 RUB from user 4821" and "Payment 5000 RUB from user
# 77931" are two payments and both must arrive. Order matters: timestamps first.
_NOISE = re.compile(
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z| UTC|[+-]\d{2}:?\d{2})?"  # timestamp
    r"|\b\d{1,2}:\d{2}:\d{2}\b"  # clock time
    r"|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"  # uuid
    r"|\b0x[0-9a-f]{8,}\b|\b(?=[0-9a-f]*[a-f])[0-9a-f]{12,}\b",  # long hex (needs a letter: a long number is an amount or an id)
    re.IGNORECASE,
)


def plain_text(text: str) -> str:
    """Tags dropped, entities decoded, whitespace collapsed."""
    return _SPACE.sub(" ", html.unescape(_TAGS.sub(" ", text or ""))).strip()


def normalize(text: str) -> str:
    """The text with markup, spacing, timestamps, UUIDs and long hex folded away; what the key is made of. Numbers stay."""
    return _NOISE.sub("#", _SPACE.sub(" ", _TAGS.sub(" ", text or "")).strip())


def fingerprint(chat_id: object, text: str) -> str:
    return hashlib.sha256(f"{chat_id}\x00{normalize(text)}".encode()).hexdigest()[:20]


def head(text: str) -> str:
    plain = plain_text(text)
    return plain if len(plain) <= HEAD_CHARS else plain[: HEAD_CHARS - 1] + "…"


# summary(count, window, head_text) is called when a window ends with repeats.
Summary = Callable[[int, int, str], None]


class _Pending:
    __slots__ = ("expires", "window", "head", "summary")

    def __init__(self, expires: float, window: int, head_text: str, summary: Summary) -> None:
        self.expires = expires
        self.window = window
        self.head = head_text
        self.summary = summary


_lock = threading.Lock()
_pending: Dict[str, _Pending] = {}
_timer: Optional[threading.Timer] = None
stats = {"suppressed_total": 0, "summaries_total": 0}


def _cache():
    from django.core.cache import cache

    return cache


def _rep_ttl(window: int) -> int:
    return max(window * 10, 600)


def gate(chat_id: object, text: str, window: int, summary: Summary) -> Tuple[bool, int]:
    """``(send, carried)``: send False drops the message as a repeat.

    ``carried`` is a count of earlier repeats whose summary never went out; the
    caller sends it as a note on this message.
    """
    if not text or window <= 0:
        return True, 0
    fp = fingerprint(chat_id, text)
    try:
        cache = _cache()
        if cache.add(f"tgdedupe:seen:{fp}", 1, window):
            rep = f"tgdedupe:rep:{fp}"
            carried = int(cache.get(rep, 0) or 0)
            if carried:
                cache.delete(rep)
            with _lock:
                if len(_pending) < MAX_TRACKED:
                    _pending[fp] = _Pending(time.time() + window + 1, window, head(text), summary)
                    _ensure_timer()
            return True, carried
        rep = f"tgdedupe:rep:{fp}"
        cache.add(rep, 0, _rep_ttl(window))
        try:
            cache.incr(rep)
        except ValueError:  # expired between add and incr
            cache.set(rep, 1, _rep_ttl(window))
        stats["suppressed_total"] += 1
        return False, 0
    except Exception:
        logger.debug("telegram dedupe cache unavailable, sending", exc_info=True)
        return True, 0


def _ensure_timer() -> None:
    """Under ``_lock``."""
    global _timer
    if _timer is None or not _timer.is_alive():
        _timer = threading.Timer(_SWEEP_SEC, flush_repeats)
        _timer.daemon = True
        _timer.start()


def flush_repeats(force: bool = False) -> int:
    """Send one summary for every ended window that has repeats. Returns summaries sent."""
    global _timer
    now = time.time()
    due = []
    with _lock:
        _timer = None
        for fp, item in list(_pending.items()):
            if force or item.expires <= now:
                due.append((fp, _pending.pop(fp)))
        if _pending:
            _ensure_timer()
    sent = 0
    for fp, item in due:
        try:
            cache = _cache()
            rep = f"tgdedupe:rep:{fp}"
            count = int(cache.get(rep, 0) or 0)
            if count <= 0:
                continue
            cache.delete(rep)
            if force:
                cache.delete(f"tgdedupe:seen:{fp}")
            item.summary(count, item.window, item.head)
            stats["summaries_total"] += 1
            sent += 1
        except Exception:
            logger.debug("telegram dedupe summary failed", exc_info=True)
    return sent


def _reset() -> None:
    """Forget pending windows (tests)."""
    global _timer
    with _lock:
        _pending.clear()
        if _timer is not None:
            _timer.cancel()
            _timer = None
    stats.update(suppressed_total=0, summaries_total=0)


__all__ = ["DEFAULT_WINDOW_SEC", "fingerprint", "flush_repeats", "gate", "normalize", "plain_text", "stats"]
