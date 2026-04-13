"""
Query budget system — tracks resource usage per agent session.

Every agent session is assigned a "Resource Budget."
If exceeded, access is revoked for the remainder of the hour.
"""

from dataclasses import dataclass
from typing import Dict, Optional

from django.core.cache import cache


@dataclass
class BudgetLimits:
    """Resource limits per agent session (per hour)."""
    max_execution_time_sec: int = 60       # Total execution time
    max_rows_fetched: int = 10_000         # Total rows returned
    max_total_cost: float = 500_000        # Total EXPLAIN cost units
    max_queries: int = 200                 # Total number of queries


class QueryBudget:
    """
    Track and enforce resource budget per agent session.

    Usage:
        budget = QueryBudget("session-123")
        if not budget.record_usage(execution_ms=100, rows=50, cost=1000):
            return "Error: Budget exceeded"
    """

    def __init__(self, session_id: str, limits: Optional[BudgetLimits] = None):
        self.session_id = session_id
        self.limits = limits or BudgetLimits()

    def _key(self, metric: str) -> str:
        return f"mcp:budget:{self.session_id}:{metric}"

    def record_usage(self, execution_ms: float, rows: int, cost: float) -> bool:
        """
        Record query usage and check limits.

        Returns:
            True if within limits, False if budget exceeded
        """
        try:
            pipe = cache.client.get_client().pipeline()
            pipe.incrbyfloat(self._key("time"), execution_ms / 1000)
            pipe.incr(self._key("rows"), rows)
            pipe.incrbyfloat(self._key("cost"), cost)
            pipe.incr(self._key("queries"))

            # Expire after 1 hour
            for i in range(4):
                pipe.expire(pipe.execute_stack()[i], 3600)

            results = pipe.execute()

            # Check limits
            time_used = results[0]
            rows_used = results[1]
            cost_used = results[2]
            queries_used = results[3]

            if time_used > self.limits.max_execution_time_sec:
                return False
            if rows_used > self.limits.max_rows_fetched:
                return False
            if cost_used > self.limits.max_total_cost:
                return False
            if queries_used > self.limits.max_queries:
                return False

            return True

        except Exception:
            # If Redis is unavailable, allow the query (fail open)
            # In production, you may want to fail closed instead
            return True

    def get_usage(self) -> Dict[str, float]:
        """Get current usage for this session."""
        return {
            "execution_time_sec": cache.get(self._key("time"), 0),
            "rows_fetched": cache.get(self._key("rows"), 0),
            "total_cost": cache.get(self._key("cost"), 0),
            "queries": cache.get(self._key("queries"), 0),
        }

    def get_remaining(self) -> Dict[str, float]:
        """Get remaining budget for this session."""
        usage = self.get_usage()
        return {
            "execution_time_sec": self.limits.max_execution_time_sec - usage["execution_time_sec"],
            "rows_fetched": self.limits.max_rows_fetched - usage["rows_fetched"],
            "total_cost": self.limits.max_total_cost - usage["total_cost"],
            "queries": self.limits.max_queries - usage["queries"],
        }

    def is_exceeded(self) -> bool:
        """Check if budget has been exceeded."""
        usage = self.get_usage()
        return (
            usage["execution_time_sec"] > self.limits.max_execution_time_sec
            or usage["rows_fetched"] > self.limits.max_rows_fetched
            or usage["total_cost"] > self.limits.max_total_cost
            or usage["queries"] > self.limits.max_queries
        )

    def reset(self) -> None:
        """Reset budget for this session."""
        for metric in ("time", "rows", "cost", "queries"):
            cache.delete(self._key(metric))
