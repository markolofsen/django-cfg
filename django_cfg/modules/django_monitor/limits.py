"""
django_monitor.limits - bounds for the public ingest endpoint.

* ``client_ip``: the address a limit is keyed on, safe against a spoofed header.
* ``within``: fixed-window counters in the Django cache (fail open).
* ``shrink_event`` / ``fit_line``: caps on one event and on one log line.

Settings (Django setting or ``DJANGO_CFG_MONITOR_*`` env):

``MONITOR_CLIENT_IP_HEADER``  header carrying the client address behind YOUR proxy
                              (``CF-Connecting-IP`` behind Cloudflare, ``X-Forwarded-For``
                              behind Traefik/nginx). Unset: the socket peer.
``MONITOR_CLIENT_IP_HOPS``    for a comma list such as X-Forwarded-For, count this many
                              entries from the RIGHT (default 1 = the entry your own
                              proxy appended; anything left of it is client-supplied).
``MONITOR_LOG_VERBOSE``       also log browser events below ``warning`` (default off).
"""
from __future__ import annotations

import ipaddress
import json
import os
import time
from typing import Any, Optional

MAX_BODY_BYTES = 64 * 1024
CLIENT_REQUESTS_PER_MIN = 60
CLIENT_EVENTS_PER_MIN = 300
PROJECT_EVENTS_PER_MIN = 3000
MAX_MESSAGE = 2000
MAX_STACK = 8000
MAX_EXTRA_BYTES = 4096
MAX_EXTRA_DEPTH = 3
MAX_LINE_BYTES = 16 * 1024

QUIET_EVENT_TYPES = frozenset({"PAGE_VIEW", "PERFORMANCE", "CONSOLE"})
QUIET_LEVELS = frozenset({"info", "debug"})


def _setting(name: str, default: Any = None) -> Any:
    try:
        from django.conf import settings

        value = getattr(settings, name, None)
        if value not in (None, ""):
            return value
    except Exception:
        pass
    value = os.environ.get(f"DJANGO_CFG_{name}", "").strip()
    return value if value else default


def _valid_ip(value: str) -> Optional[str]:
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None


def peer_address(request) -> str:
    """The address that opened the socket (set by RealIPMiddleware before it rewrites REMOTE_ADDR)."""
    return request.META.get("DJANGO_CFG_PEER_ADDR") or request.META.get("REMOTE_ADDR", "") or ""


def client_ip(request) -> str:
    """Address to key limits and logs on.

    With ``MONITOR_CLIENT_IP_HEADER`` set, that header is read from the right
    (``MONITOR_CLIENT_IP_HOPS``), so a value the visitor put in front of what the
    proxy appended is ignored. A missing, short or non-IP header falls back to the
    socket peer. Never the first ``X-Forwarded-For`` entry, which any client chooses.
    """
    header = _setting("MONITOR_CLIENT_IP_HEADER")
    if header:
        raw = request.META.get("HTTP_" + str(header).upper().replace("-", "_"), "")
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        try:
            hops = max(1, int(_setting("MONITOR_CLIENT_IP_HOPS", 1)))
        except (TypeError, ValueError):
            hops = 1
        if len(parts) >= hops:
            ip = _valid_ip(parts[-hops])
            if ip:
                return ip
    return peer_address(request)


def verbose() -> bool:
    return str(_setting("MONITOR_LOG_VERBOSE", "")).strip().lower() in ("1", "true", "yes", "on")


def worth_logging(event: dict) -> bool:
    """Browser events below ``warning`` are noise unless asked for. A ping is always kept."""
    extra = event.get("extra")
    if isinstance(extra, dict) and extra.get("ping"):
        return True
    if verbose():
        return True
    if event.get("event_type") in QUIET_EVENT_TYPES:
        return False
    return event.get("level") not in QUIET_LEVELS


def within(scope: str, ident: str, amount: int, limit: int, window: int = 60) -> bool:
    """Add ``amount`` to a fixed-window counter; True while the total is within ``limit``.

    Fails open: a cache error never turns an honest event into a refusal.
    """
    try:
        from django.core.cache import cache

        key = f"cfgmon:{scope}:{ident}:{int(time.time() // window)}"
        cache.add(key, 0, window * 2)
        return cache.incr(key, amount) <= limit
    except Exception:
        return True


def record_dropped(count: int) -> None:
    """Count events refused by the project ceiling; log one line per minute."""
    try:
        from django.core.cache import cache

        bucket = int(time.time() // 60)
        key = f"cfgmon:dropped:{bucket}"
        cache.add(key, 0, 3600)
        total = cache.incr(key, count)
        cache.add("cfgmon:dropped:total", 0, 7 * 86400)
        cache.incr("cfgmon:dropped:total", count)
        if cache.add(f"cfgmon:dropped:logged:{bucket}", 1, 120):
            from django_cfg.modules.django_monitor import _log_event

            _log_event("dropped", {
                "event_type": "MONITOR_DROPPED",
                "level": "warning",
                "message": f"ingest ceiling of {PROJECT_EVENTS_PER_MIN} events/min reached; dropping browser events",
                "count": total,
            })
    except Exception:
        pass


def dropped_counts() -> dict:
    """``{"last_minute": n, "total": n}`` read back from the cache (0 when unavailable)."""
    try:
        from django.core.cache import cache

        bucket = int(time.time() // 60)
        return {
            "last_minute": int(cache.get(f"cfgmon:dropped:{bucket}", 0) or 0),
            "total": int(cache.get("cfgmon:dropped:total", 0) or 0),
        }
    except Exception:
        return {"last_minute": 0, "total": 0}


def _clip(value: Any, depth: int) -> Any:
    if isinstance(value, dict):
        if depth <= 0:
            return "[truncated]"
        return {str(k)[:100]: _clip(v, depth - 1) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        if depth <= 0:
            return "[truncated]"
        return [_clip(v, depth - 1) for v in value]
    return value


def shrink_event(event: dict) -> dict:
    """Apply the per-event caps in place-safe fashion; sets ``truncated`` when anything was cut."""
    out = dict(event)
    cut = False
    for key, cap in (("message", MAX_MESSAGE), ("stack_trace", MAX_STACK)):
        value = out.get(key)
        if isinstance(value, str) and len(value) > cap:
            out[key] = value[:cap]
            cut = True
    extra = out.get("extra")
    if extra:
        clipped = _clip(extra, MAX_EXTRA_DEPTH)
        try:
            encoded = json.dumps(clipped, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            encoded = ""
            clipped = {"_unserialisable": True}
            cut = True
        if len(encoded.encode()) > MAX_EXTRA_BYTES:
            clipped = {"_truncated": True, "_bytes": len(encoded.encode())}
            cut = True
        elif clipped != extra:
            cut = True
        out["extra"] = clipped
    if cut:
        out["truncated"] = True
    return out


def fit_line(record: dict) -> dict:
    """Keep one serialised event under ``MAX_LINE_BYTES``: drop ``extra``, then shorten the rest."""

    def size(r: dict) -> int:
        return len(json.dumps(r, ensure_ascii=False, default=str).encode())

    if size(record) <= MAX_LINE_BYTES:
        return record
    out = dict(record)
    out["truncated"] = True
    for step in ("extra", "stack_trace", "message"):
        if step == "extra":
            out.pop("extra", None)
        elif step == "stack_trace" and isinstance(out.get("stack_trace"), str):
            out["stack_trace"] = out["stack_trace"][:2000]
        elif isinstance(out.get("message"), str):
            out["message"] = out["message"][:500]
        if size(out) <= MAX_LINE_BYTES:
            return out
    for key in list(out):
        if isinstance(out[key], str) and len(out[key]) > 500:
            out[key] = out[key][:500]
    return out


__all__ = [
    "MAX_BODY_BYTES",
    "client_ip",
    "dropped_counts",
    "fit_line",
    "peer_address",
    "record_dropped",
    "shrink_event",
    "within",
    "worth_logging",
]
