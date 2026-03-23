"""
django_cf.core.usage — D1 daily usage tracker.

In-memory counter that tracks rows read/written per UTC day.
Resets automatically at midnight UTC. Thread-safe.

Used by CloudflareD1Client.execute() to:
1. Skip queries when daily limit is reached (returns empty D1QueryResult)
2. Log WARNING when usage crosses the configured threshold (e.g. 80%)

No external state — counters reset on process restart or UTC day rollover.
This means usage is tracked per-process, not globally. For multi-process
deployments, actual D1 usage may be higher than any single process tracks.
This is acceptable — the tracker is a best-effort safety net, not billing.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import date, timezone as dt_timezone

logger = logging.getLogger(__name__)


@dataclass
class _DayCounters:
    """Counters for a single UTC day."""

    day: date
    reads: int = 0
    writes: int = 0
    read_warned: bool = False
    write_warned: bool = False


class D1UsageTracker:
    """Thread-safe daily usage tracker for D1 reads/writes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters = _DayCounters(day=self._today())

    @staticmethod
    def _today() -> date:
        from datetime import datetime
        return datetime.now(dt_timezone.utc).date()

    def _get_counters(self) -> _DayCounters:
        """Return counters for today, resetting if day changed."""
        today = self._today()
        if self._counters.day != today:
            self._counters = _DayCounters(day=today)
        return self._counters

    def record_read(self, rows: int = 1) -> None:
        """Record rows read from D1."""
        with self._lock:
            c = self._get_counters()
            c.reads += rows

    def record_write(self, rows: int = 1) -> None:
        """Record rows written to D1."""
        with self._lock:
            c = self._get_counters()
            c.writes += rows

    def check_read_limit(self, limit: int, warn_pct: int = 80) -> bool:
        """Check if reads are within limit. Returns True if OK, False if exceeded.

        Logs WARNING once when crossing warn_pct threshold.
        """
        if limit <= 0:
            return True  # unlimited
        with self._lock:
            c = self._get_counters()
            if c.reads >= limit:
                return False
            if warn_pct > 0 and not c.read_warned and c.reads >= limit * warn_pct // 100:
                c.read_warned = True
                logger.warning(
                    "django_cf: D1 daily READ usage at %d%% (%d / %d)",
                    c.reads * 100 // limit, c.reads, limit,
                )
            return True

    def check_write_limit(self, limit: int, warn_pct: int = 80) -> bool:
        """Check if writes are within limit. Returns True if OK, False if exceeded.

        Logs WARNING once when crossing warn_pct threshold.
        """
        if limit <= 0:
            return True  # unlimited
        with self._lock:
            c = self._get_counters()
            if c.writes >= limit:
                return False
            if warn_pct > 0 and not c.write_warned and c.writes >= limit * warn_pct // 100:
                c.write_warned = True
                logger.warning(
                    "django_cf: D1 daily WRITE usage at %d%% (%d / %d)",
                    c.writes * 100 // limit, c.writes, limit,
                )
            return True

    def get_usage(self) -> dict[str, int | str]:
        """Return current daily usage snapshot."""
        with self._lock:
            c = self._get_counters()
            return {"reads": c.reads, "writes": c.writes, "day": str(c.day)}


# Singleton — shared by all D1 clients in this process
usage_tracker = D1UsageTracker()

__all__ = ["D1UsageTracker", "usage_tracker"]
