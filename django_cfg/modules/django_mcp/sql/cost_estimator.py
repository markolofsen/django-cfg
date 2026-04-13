"""
Query cost estimation via EXPLAIN (FORMAT JSON).

Rejects queries exceeding cost threshold before execution.
"""

import json
from typing import Any, Dict, Optional
from django.db import connection


class CostExceededError(Exception):
    """Raised when query cost exceeds threshold."""

    def __init__(self, cost: float, threshold: float, hint: str = ""):
        self.cost = cost
        self.threshold = threshold
        self.hint = hint
        super().__init__(f"Query cost {cost:.0f} exceeds limit {threshold:.0f}. {hint}")


class QueryCostEstimator:
    """
    Estimate query cost via EXPLAIN before execution.

    Usage:
        estimator = QueryCostEstimator(max_cost=50_000)
        info = estimator.estimate("SELECT * FROM orders WHERE status = %s", ('active',))
    """

    DEFAULT_MAX_COST = 50_000
    DEFAULT_MAX_ROWS = 10_000
    DEFAULT_TIMEOUT_MS = 5000

    def __init__(
        self,
        max_cost: float = DEFAULT_MAX_COST,
        max_rows: float = DEFAULT_MAX_ROWS,
    ):
        self.max_cost = max_cost
        self.max_rows = max_rows

    def estimate(
        self,
        sql: str,
        params: tuple = None,
        database: str = 'default',
    ) -> Dict[str, Any]:
        """
        Run EXPLAIN and return cost analysis.

        Args:
            sql: SQL query (without EXPLAIN prefix)
            params: Query parameters for binding
            database: Django database alias

        Returns:
            dict with total_cost, plan_rows, plan_type, scan_type

        Raises:
            CostExceededError: If query exceeds thresholds
        """
        explain_sql = f"EXPLAIN (FORMAT JSON) {sql}"

        try:
            with connection.cursor() as cursor:
                cursor.execute(explain_sql, params or ())
                result = cursor.fetchone()[0]
        except Exception as e:
            # EXPLAIN failed — query is invalid
            raise CostExceededError(
                cost=0,
                threshold=self.max_cost,
                hint=f"Query is invalid: {str(e)}",
            )

        if not result or not isinstance(result, list) or len(result) == 0:
            raise CostExceededError(
                cost=0,
                threshold=self.max_cost,
                hint="EXPLAIN returned empty result",
            )

        plan = result[0].get('Plan', {})
        total_cost = plan.get('Total Cost', 0)
        plan_rows = plan.get('Plan Rows', 0)

        # Check thresholds
        if total_cost > self.max_cost:
            hint = self._generate_hint(plan)
            raise CostExceededError(total_cost, self.max_cost, hint)

        if plan_rows > self.max_rows:
            hint = "Add a WHERE clause on an indexed column or use LIMIT."
            raise CostExceededError(total_cost, self.max_rows, hint)

        return {
            "total_cost": round(total_cost, 2),
            "plan_rows": int(plan_rows),
            "plan_type": plan.get("Node Type", "unknown"),
            "scan_type": self._get_scan_type(plan),
        }

    def _generate_hint(self, plan: Dict) -> str:
        """Generate actionable hint for cost rejection."""
        node_type = plan.get("Node Type", "")
        plan_rows = plan.get("Plan Rows", 0)

        if "Seq Scan" in node_type:
            return "Full table scan detected. Add WHERE clause on indexed column."
        if "Nested Loop" in node_type and plan_rows > 10_000:
            return "Cartesian product likely. Check JOIN conditions."
        if "Hash Join" in node_type and plan_rows > 100_000:
            return "Large join detected. Reduce result set with filters."
        if "Materialize" in node_type:
            return "Subquery materialization detected. Optimize subquery."
        if "Sort" in node_type and plan_rows > 50_000:
            return "Large sort detected. Add ORDER BY on indexed column."

        return f"Query too complex (cost: {plan.get('Total Cost', 0):.0f}). Simplify or add indexed filters."

    def _get_scan_type(self, plan: Dict) -> str:
        """Determine scan type for audit logging."""
        node_type = plan.get("Node Type", "")

        if "Seq Scan" in node_type:
            return "sequential"
        if "Index Scan" in node_type or "Index Only Scan" in node_type:
            return "index"
        if "Bitmap" in node_type:
            return "bitmap"
        if "Hash" in node_type:
            return "hash"
        if "Nested Loop" in node_type:
            return "nested_loop"

        return node_type.lower()

    def estimate_multiple(
        self,
        queries: list,
    ) -> Dict[str, Any]:
        """
        Estimate cost for multiple queries.

        Args:
            queries: List of (sql, params) tuples

        Returns:
            dict with per-query results and total cost
        """
        results = []
        total_cost = 0
        total_rows = 0

        for sql, params in queries:
            try:
                info = self.estimate(sql, params)
                results.append({
                    "sql": sql[:100],
                    "cost": info["total_cost"],
                    "rows": info["plan_rows"],
                    "scan_type": info["scan_type"],
                    "status": "ok",
                })
                total_cost += info["total_cost"]
                total_rows += info["plan_rows"]
            except CostExceededError as e:
                results.append({
                    "sql": sql[:100],
                    "cost": e.cost,
                    "status": "exceeded",
                    "hint": e.hint,
                })

        return {
            "queries": results,
            "total_cost": round(total_cost, 2),
            "total_rows": total_rows,
            "passed": sum(1 for r in results if r.get("status") == "ok"),
            "failed": sum(1 for r in results if r.get("status") == "exceeded"),
        }
