"""
Agent Query Context — tracks complexity and enforces limits.

Prevents heavy queries from degrading performance:
- Max tool calls per session
- Max rows returned
- Max query depth (FK traversals)
- Execution timeout
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class QueryRecord:
    """Record of a single query for audit/tracking."""
    tool: str
    model: Optional[str]  # app.Model or None for raw SQL
    params: Dict[str, Any] = field(default_factory=dict)
    rows_returned: int = 0
    execution_ms: float = 0
    error: Optional[str] = None


@dataclass
class AgentQueryContext:
    """
    Shared context for an agent session.
    Enforces limits to prevent heavy queries.
    """

    # Accumulated state
    queries: List[QueryRecord] = field(default_factory=list)
    tool_calls: int = 0
    total_rows_fetched: int = 0
    max_depth_reached: int = 0

    # Limits (configurable)
    max_tool_calls: int = 20
    max_total_rows: int = 1000  # total rows across all queries
    max_rows_per_query: int = 100  # per single query
    max_query_depth: int = 3  # FK traversal depth
    max_raw_sql_time_ms: float = 5000  # timeout for raw SQL

    # Tenant isolation
    tenant_id: Optional[str] = None

    def can_call_tool(self) -> bool:
        return self.tool_calls < self.max_tool_calls

    def can_fetch_rows(self, count: int) -> bool:
        return (self.total_rows_fetched + count) <= self.max_total_rows

    def record_query(
        self,
        tool: str,
        model: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        rows: int = 0,
        ms: float = 0,
        error: Optional[str] = None,
    ) -> None:
        self.tool_calls += 1
        self.total_rows_fetched += rows
        self.queries.append(QueryRecord(
            tool=tool,
            model=model,
            params=params or {},
            rows_returned=rows,
            execution_ms=ms,
            error=error,
        ))

    def record_depth(self, depth: int) -> None:
        if depth > self.max_depth_reached:
            self.max_depth_reached = depth

    def summary(self) -> Dict[str, Any]:
        return {
            "tool_calls": self.tool_calls,
            "total_rows_fetched": self.total_rows_fetched,
            "max_depth_reached": self.max_depth_reached,
            "queries": len(self.queries),
        }
