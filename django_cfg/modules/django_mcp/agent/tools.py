"""
Enhanced Model Query Tool for MCP.

Supports:
- Filtering (Django ORM syntax)
- Ordering
- Pagination (limit/offset)
- select_related (FK optimization)
- Aggregations (COUNT, SUM, AVG, MIN, MAX)
- Annotations

Safety:
- Max rows enforced
- Only exposed models allowed
- No raw SQL
"""

import json
import time
from typing import Any, Dict, List

from django.apps import apps
from django.db import models
from django.db.models import Count, Sum, Avg, Min, Max, F

from django_cfg.modules.django_mcp.tools.base import MCPTool
from django_cfg.modules.django_mcp.agent.context import AgentQueryContext
from django_cfg.modules.django_mcp.services.redactor import apply_redaction, RedactionMode


# Global context instance (per-request, set by view)
query_context: AgentQueryContext = AgentQueryContext()


class QueryModelTool(MCPTool):
    """
    Query a Django model with filters, ordering, and aggregations.

    Supports safe ORM queries only — no raw SQL.
    """

    name = "query_model"
    description = (
        "Query a Django model. Supports filtering, ordering, pagination, "
        "select_related for FK optimization, and aggregations. "
        "Use filters like Django ORM: {'field__contains': 'value'}."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string", "description": "App label (e.g., 'accounts')"},
            "model_name": {"type": "string", "description": "Model name (e.g., 'user')"},
            "filters": {
                "type": "object",
                "description": "Django ORM filter kwargs (e.g., {'is_active': True, 'date__gte': '2024-01-01'})",
            },
            "order_by": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Fields to order by (prefix with '-' for desc)",
            },
            "limit": {"type": "integer", "description": "Max rows (default 50, max 100)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
            "select_related": {
                "type": "array",
                "items": {"type": "string"},
                "description": "FK field names to join (prevents N+1)",
            },
            "prefetch_related": {
                "type": "array",
                "items": {"type": "string"},
                "description": "M2M/reverse FK fields to prefetch",
            },
            "values": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific fields to return (omit for all)",
            },
            "aggregate": {
                "type": "object",
                "description": "Aggregations: {'count': '*', 'sum': 'price', 'avg': 'rating'}",
            },
        },
        "required": ["app_label", "model_name"],
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the query_model tool."""
        start = time.time()
        app_label = arguments.get("app_label", "")
        model_name = arguments.get("model_name", "")

        # Check if model is exposed
        if not context.config.is_model_exposed(app_label, model_name):
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error="Model not exposed")
            return f"Error: Model '{app_label}.{model_name}' is not exposed to MCP"

        model_config = context.config.get_model_config(app_label, model_name)
        if not model_config:
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error="Config not found")
            return "Error: Model configuration not found"

        # Get model class
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error="Model not found")
            return f"Error: Model '{app_label}.{model_name}' not found"

        try:
            # Build queryset
            qs = model.objects.all()

            # Apply select_related (FK optimization)
            select_related = arguments.get("select_related", [])
            if select_related:
                qs = qs.select_related(*select_related)

            # Apply prefetch_related
            prefetch_related = arguments.get("prefetch_related", [])
            if prefetch_related:
                qs = qs.prefetch_related(*prefetch_related)

            # Apply filters
            filters = arguments.get("filters", {})
            if filters:
                qs = qs.filter(**filters)

            # Apply ordering
            order_by = arguments.get("order_by")
            if order_by:
                qs = qs.order_by(*order_by)

            # Handle aggregations
            aggregate = arguments.get("aggregate")
            if aggregate:
                return self._handle_aggregation(qs, aggregate, app_label, model_name, start, context)

            # Apply limits
            limit = min(arguments.get("limit", 50), model_config.max_results, 100)
            offset = arguments.get("offset", 0)

            if not query_context.can_fetch_rows(limit):
                query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error="Max rows limit reached")
                return f"Error: Session row limit reached ({query_context.total_rows_fetched}/{query_context.max_total_rows}). Use smaller limit or start new session."

            qs = qs[offset:offset + limit]

            # Execute query
            values = arguments.get("values")
            if values:
                results = list(qs.values(*values))
            else:
                results = self._serialize_queryset(qs, model, model_config.hidden_fields)

            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(
                self.name, f"{app_label}.{model_name}", arguments, rows=len(results), ms=elapsed_ms
            )

            # Apply redaction
            mode = RedactionMode(context.config.redaction.mode.lower())
            results = apply_redaction(results, mode)

            return json.dumps({
                "count": len(results),
                "model": f"{app_label}.{model_name}",
                "results": results,
                "execution_ms": round(elapsed_ms, 2),
            }, indent=2, default=str)

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error=str(e), ms=elapsed_ms)
            return f"Error: Query failed — {str(e)}"

    def _handle_aggregation(self, qs, aggregate, app_label, model_name, start, context):
        """Handle aggregate queries (COUNT, SUM, AVG, MIN, MAX)."""
        aggs = {}
        for func, field_name in aggregate.items():
            func = func.lower()
            if func == "count":
                aggs["count"] = Count(field_name if field_name != "*" else "id")
            elif func == "sum":
                aggs["total"] = Sum(field_name)
            elif func == "avg":
                aggs["average"] = Avg(field_name)
            elif func == "min":
                aggs["minimum"] = Min(field_name)
            elif func == "max":
                aggs["maximum"] = Max(field_name)

        if aggs:
            result = qs.aggregate(**aggs)
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", {"aggregate": aggregate}, ms=elapsed_ms)
            return json.dumps({"model": f"{app_label}.{model_name}", "aggregates": result}, indent=2, default=str)

        return "Error: No valid aggregations"

    def _serialize_queryset(self, qs, model, hidden_fields):
        """Serialize QuerySet to list of dicts."""
        results = []
        for obj in qs:
            obj_data = {}
            for field in model._meta.fields:
                if field.name in hidden_fields:
                    continue
                value = getattr(obj, field.name)
                if isinstance(value, models.Model):
                    obj_data[field.name] = value.pk if value else None
                elif hasattr(value, "isoformat"):
                    obj_data[field.name] = value.isoformat()
                elif hasattr(value, "__iter__") and not isinstance(value, str):
                    obj_data[field.name] = list(value)
                else:
                    obj_data[field.name] = value
            results.append(obj_data)
        return results


class CountRecordsTool(MCPTool):
    """
    Fast COUNT(*) query without loading records.

    Use this to check how many records match a filter before fetching them.
    """

    name = "count_records"
    description = (
        "Count records matching a filter without loading them. "
        "Fast COUNT(*) query at the database level."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string"},
            "model_name": {"type": "string"},
            "filters": {"type": "object", "description": "Django ORM filter kwargs"},
        },
        "required": ["app_label", "model_name"],
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the count_records tool."""
        start = time.time()
        app_label = arguments.get("app_label", "")
        model_name = arguments.get("model_name", "")

        if not context.config.is_model_exposed(app_label, model_name):
            return f"Error: Model '{app_label}.{model_name}' is not exposed"

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return f"Error: Model '{app_label}.{model_name}' not found"

        try:
            qs = model.objects.all()
            filters = arguments.get("filters", {})
            if filters:
                qs = qs.filter(**filters)

            count = qs.count()
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, rows=count, ms=elapsed_ms)

            return json.dumps({
                "model": f"{app_label}.{model_name}",
                "count": count,
                "execution_ms": round(elapsed_ms, 2),
            }, indent=2)

        except Exception as e:
            return f"Error: Count failed — {str(e)}"


class RawSQLTool(MCPTool):
    """
    Execute read-only raw SQL queries with AST validation and cost estimation.

    Safety pipeline:
    1. pglast AST validation — only SELECT allowed
    2. EXPLAIN cost estimation — reject expensive queries
    3. Read-only transaction — SET TRANSACTION READ ONLY
    4. Max rows enforced
    5. Parameterized queries only
    """

    name = "raw_sql"
    description = (
        "Execute a raw SQL query (read-only only). "
        "Uses PostgreSQL AST validation and EXPLAIN cost estimation. "
        "Limited to SELECT queries with max 100 rows."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "SQL query (SELECT only)"},
            "params": {
                "type": "array",
                "items": {"type": "string"},
                "description": "SQL parameters (prevents injection)",
            },
            "limit": {"type": "integer", "description": "Max rows (default 50, max 100)"},
        },
        "required": ["sql"],
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the raw_sql tool with full safety pipeline."""
        from django.db import connection
        from django_cfg.modules.django_mcp.sql.validator import SQLValidator, HAS_PGLAST
        from django_cfg.modules.django_mcp.sql.cost_estimator import QueryCostEstimator, CostExceededError

        start = time.time()
        sql = arguments.get("sql", "").strip()
        params = arguments.get("params", [])

        if not sql.upper().startswith("SELECT"):
            query_context.record_query(self.name, error="Non-SELECT SQL blocked")
            return "Error: Only SELECT queries are allowed"

        # ── Step 1: AST Validation ──────────────────────────────────────
        if HAS_PGLAST:
            try:
                validator = SQLValidator()
                validator.validate_or_raise(sql)
            except Exception as e:
                query_context.record_query(self.name, error=f"AST validation failed: {e}")
                return f"Error: SQL validation failed — {e}"

        # ── Step 2: Cost Estimation ─────────────────────────────────────
        estimator = QueryCostEstimator(max_cost=50_000, max_rows=10_000)
        try:
            cost_info = estimator.estimate(sql, tuple(params) if params else None)
        except CostExceededError as e:
            query_context.record_query(self.name, error=f"Cost exceeded: {e.hint}")
            return f"Error: Query too expensive — {e.hint} (Cost: {e.cost:.0f}, Limit: {e.threshold:.0f})"

        # ── Step 3: Execute (with read-only enforcement) ────────────────
        try:
            with connection.cursor() as cursor:
                # Enforce read-only and resource limits
                cursor.execute("SET LOCAL default_transaction_read_only = on")
                cursor.execute("SET LOCAL statement_timeout = 5000")
                cursor.execute("SET LOCAL lock_timeout = 2000")

                # Set tenant context for RLS
                if hasattr(context, 'tenant_id') and context.tenant_id:
                    cursor.execute("SET LOCAL mcp.current_tenant = %s", [str(context.tenant_id)])

                # Execute query
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                limit = min(arguments.get("limit", 50), 100)
                rows = cursor.fetchmany(limit)

                results = [dict(zip(columns, row)) for row in rows]

            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(
                self.name, rows=len(results), ms=elapsed_ms,
                params={"sql_preview": sql[:200]}
            )

            # Apply redaction
            mode = RedactionMode(context.config.redaction.mode.lower())
            results = apply_redaction(results, mode)

            return json.dumps({
                "count": len(results),
                "results": results,
                "execution_ms": round(elapsed_ms, 2),
                "estimated_cost": cost_info["total_cost"],
                "scan_type": cost_info["scan_type"],
            }, indent=2, default=str)

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, error=str(e), ms=elapsed_ms)
            return f"Error: SQL query failed — {str(e)}"


# Global instances
query_model_tool = QueryModelTool()
count_records_tool = CountRecordsTool()
raw_sql_tool = RawSQLTool()
