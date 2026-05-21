"""
Redis-backed alert dedup / cooldown for the RQ queue-health monitor.

The monitor runs as a periodic RQ job that may execute on different worker
processes between cycles, so cooldown state must live in Redis rather than
in-process.

Keys
----
``dcfg:rq_health:alert_cooldown:<queue>:<severity>``
    Set with ``SET ... NX EX <cooldown>``. While it exists, an alert of that
    ``(queue, severity)`` is suppressed.

``dcfg:rq_health:alerting:<queue>``
    A marker that the queue is currently in an alerting state. Used so a
    recovery message is only sent for queues that actually alerted.

Escalation
----------
A ``critical`` alert fires even inside a ``warning`` cooldown — :func:`should_alert`
checks the ``critical`` cooldown key for critical severities and ignores any
warning cooldown.
"""

from __future__ import annotations

from django_cfg.utils import get_logger

from .evaluator import Severity

logger = get_logger("rq.health")

_KEY_PREFIX = "dcfg:rq_health"


def _cooldown_key(queue: str, severity: Severity) -> str:
    return f"{_KEY_PREFIX}:alert_cooldown:{queue}:{severity.label}"


def _alerting_key(queue: str) -> str:
    return f"{_KEY_PREFIX}:alerting:{queue}"


def should_alert(redis_conn, queue: str, severity: Severity, cooldown_sec: int) -> bool:
    """
    Atomically decide whether an alert may be sent, and arm the cooldown.

    Uses ``SET key 1 NX EX cooldown`` — when the key did not exist it is created
    and ``True`` is returned; when it already existed ``False`` is returned.

    For ``CRITICAL`` severity only the critical cooldown key is consulted, so a
    critical alert escalates past an active warning cooldown.

    Args:
        redis_conn: Redis connection.
        queue: Queue name.
        severity: Alert severity (WARNING or CRITICAL).
        cooldown_sec: Cooldown duration in seconds.

    Returns:
        True if the alert should be sent now, False if suppressed by cooldown.
    """
    key = _cooldown_key(queue, severity)
    try:
        acquired = redis_conn.set(key, "1", nx=True, ex=cooldown_sec)
        return bool(acquired)
    except Exception as exc:  # pragma: no cover - defensive
        # If Redis is unavailable, fail open (send the alert) — better a
        # duplicate alert than a missed one.
        logger.warning(f"cooldown check failed for '{queue}'/{severity.label}: {exc}")
        return True


def mark_alerted(redis_conn, queue: str) -> None:
    """Record that ``queue`` is in an alerting state (drives recovery messages)."""
    try:
        redis_conn.set(_alerting_key(queue), "1")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"failed to mark '{queue}' alerting: {exc}")


def is_alerting(redis_conn, queue: str) -> bool:
    """Return True if ``queue`` is currently flagged as alerting."""
    try:
        return bool(redis_conn.exists(_alerting_key(queue)))
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"failed to read alerting flag for '{queue}': {exc}")
        return False


def mark_recovered(redis_conn, queue: str) -> None:
    """
    Clear all alert state for ``queue`` after it returns to healthy.

    Deletes the alerting marker and both severity cooldown keys so the next
    degradation alerts immediately.
    """
    try:
        redis_conn.delete(
            _alerting_key(queue),
            _cooldown_key(queue, Severity.WARNING),
            _cooldown_key(queue, Severity.CRITICAL),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"failed to clear alert state for '{queue}': {exc}")


__all__ = [
    "should_alert",
    "mark_alerted",
    "is_alerting",
    "mark_recovered",
]
