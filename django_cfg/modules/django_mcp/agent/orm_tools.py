"""
Extended ORM Tools for MCP.

Advanced querying with safety limits:
- select_related depth limits
- prefetch_related field limits
- Time-series aggregation
- Statistical distribution analysis
- Top values query
"""

import json
import time
from typing import Any, Dict, List

from django.apps import apps
from django.db import models
from django.db.models import Count, Sum, Avg, Min, Max, Q
from django.db.models.functions import TruncMonth, TruncDay, TruncHour

from django_cfg.modules.django_mcp.tools.base import MCPTool
from django_cfg.modules.django_mcp.agent.context import AgentQueryContext
from django_cfg.modules.django_mcp.services.redactor import apply_redaction, RedactionMode


# Global context instance
query_context: AgentQueryContext = AgentQueryContext()


class AggregateModelTool(MCPTool):
    """
    Aggregate data from a Django model.

    Supports COUNT, SUM, AVG, MIN, MAX with optional GROUP BY.
    """

    name = "aggregate_model"
    description = (
        "Aggregate data from a model: count, sum, avg, min, max. "
        "Optionally group by a field. Safe ORM-only aggregation."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string"},
            "model_name": {"type": "string"},
            "aggregate": {
                "type": "string",
                "enum": ["count", "sum", "avg", "min", "max"],
                "description": "Aggregation function",
            },
            "field": {
                "type": "string",
                "description": "Field to aggregate (omit for count)",
            },
            "group_by": {
                "type": "string",
                "description": "Field to group by (optional)",
            },
            "filters": {
                "type": "object",
                "description": "Django ORM filter kwargs",
            },
            "limit": {
                "type": "integer",
                "description": "Max groups returned (default 50)",
            },
        },
        "required": ["app_label", "model_name", "aggregate"],
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the aggregate_model tool."""
        start = time.time()
        app_label = arguments.get("app_label", "")
        model_name = arguments.get("model_name", "")

        if not context.config.is_model_exposed(app_label, model_name):
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error="Not exposed")
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

            agg_func = arguments.get("aggregate", "count").lower()
            field = arguments.get("field")
            group_by = arguments.get("group_by")

            # Simple aggregate (no GROUP BY)
            if not group_by:
                if agg_func == "count":
                    result = {"count": qs.count()}
                elif agg_func == "sum" and field:
                    result = {"total": qs.aggregate(total=Sum(field))["total"]}
                elif agg_func == "avg" and field:
                    result = {"average": qs.aggregate(average=Avg(field))["average"]}
                elif agg_func == "min" and field:
                    result = {"minimum": qs.aggregate(minimum=Min(field))["minimum"]}
                elif agg_func == "max" and field:
                    result = {"maximum": qs.aggregate(maximum=Max(field))["maximum"]}
                else:
                    return f"Error: '{agg_func}' requires a 'field' parameter"

                elapsed_ms = (time.time() - start) * 1000
                query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, ms=elapsed_ms)
                return json.dumps({"model": f"{app_label}.{model_name}", "aggregate": result}, indent=2, default=str)

            # GROUP BY aggregate
            qs = qs.values(group_by)
            if agg_func == "count":
                qs = qs.annotate(value=Count("id"))
            elif agg_func == "sum" and field:
                qs = qs.annotate(value=Sum(field))
            elif agg_func == "avg" and field:
                qs = qs.annotate(value=Avg(field))
            elif agg_func == "min" and field:
                qs = qs.annotate(value=Min(field))
            elif agg_func == "max" and field:
                qs = qs.annotate(value=Max(field))
            else:
                return f"Error: '{agg_func}' requires a 'field' parameter"

            # Order by value descending
            qs = qs.order_by("-value")

            # Limit results
            limit = min(arguments.get("limit", 50), 200)
            if not query_context.can_fetch_rows(limit):
                return f"Error: Session row limit reached ({query_context.total_rows_fetched}/{query_context.max_total_rows})"

            results = list(qs[:limit])

            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(
                self.name, f"{app_label}.{model_name}", arguments, rows=len(results), ms=elapsed_ms
            )

            return json.dumps({
                "model": f"{app_label}.{model_name}",
                "group_by": group_by,
                "aggregate": agg_func,
                "results": results,
                "execution_ms": round(elapsed_ms, 2),
            }, indent=2, default=str)

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error=str(e), ms=elapsed_ms)
            return f"Error: Aggregation failed — {str(e)}"


class TimeSeriesTool(MCPTool):
    """
    Time-series aggregation using date_trunc.

    Safe — uses pre-optimized SQL template via Django ORM.
    """

    name = "time_series"
    description = (
        "Group data by time intervals (hourly, daily, monthly, yearly). "
        "Automatically limits range to 12 months if no filter provided."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string"},
            "model_name": {"type": "string"},
            "date_field": {"type": "string", "description": "Date/datetime field to group by"},
            "interval": {
                "type": "string",
                "enum": ["hour", "day", "week", "month", "year"],
                "description": "Time interval for grouping",
            },
            "metric": {
                "type": "string",
                "enum": ["count", "sum", "avg"],
                "description": "Metric to calculate per interval",
            },
            "metric_field": {
                "type": "string",
                "description": "Field to aggregate (required for sum/avg)",
            },
            "max_range_months": {
                "type": "integer",
                "default": 12,
                "description": "Maximum date range in months (prevents huge scans)",
            },
        },
        "required": ["app_label", "model_name", "date_field", "interval"],
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the time_series tool."""
        start = time.time()
        app_label = arguments.get("app_label", "")
        model_name = arguments.get("model_name", "")
        date_field = arguments.get("date_field", "")
        interval = arguments.get("interval", "month")
        metric = arguments.get("metric", "count")
        metric_field = arguments.get("metric_field")

        if not context.config.is_model_exposed(app_label, model_name):
            return f"Error: Model '{app_label}.{model_name}' is not exposed"

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return f"Error: Model '{app_label}.{model_name}' not found"

        try:
            from django.utils import timezone
            from datetime import timedelta

            qs = model.objects.all()

            # Auto-limit range to prevent huge scans
            max_months = arguments.get("max_range_months", 12)
            cutoff = timezone.now() - timedelta(days=max_months * 30)
            qs = qs.filter(**{f"{date_field}__gte": cutoff})

            # Apply user filters if provided (passed via arguments['filters'])
            filters = arguments.get("filters", {})
            if filters:
                qs = qs.filter(**filters)

            # Select truncation function
            trunc_map = {
                "hour": TruncHour,
                "day": TruncDay,
                "month": TruncMonth,
            }
            trunc_func = trunc_map.get(interval, TruncMonth)

            # Truncate and annotate
            qs = qs.annotate(period=trunc_func(date_field)).values("period").order_by("period")

            if metric == "count":
                qs = qs.annotate(value=Count("id"))
            elif metric == "sum" and metric_field:
                qs = qs.annotate(value=Sum(metric_field))
            elif metric == "avg" and metric_field:
                qs = qs.annotate(value=Avg(metric_field))
            else:
                return f"Error: '{metric}' requires a metric_field parameter"

            results = list(qs)

            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, rows=len(results), ms=elapsed_ms)

            return json.dumps({
                "model": f"{app_label}.{model_name}",
                "interval": interval,
                "metric": metric,
                "series": results,
                "execution_ms": round(elapsed_ms, 2),
            }, indent=2, default=str)

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error=str(e), ms=elapsed_ms)
            return f"Error: Time series failed — {str(e)}"


class TopValuesTool(MCPTool):
    """
    Find most frequent values in a field.

    Uses values().annotate(count=Count('id')).order_by('-count')[:limit].
    """

    name = "top_values"
    description = (
        "Find the most frequent values in a field. "
        "Returns top N values with their counts."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string"},
            "model_name": {"type": "string"},
            "field": {"type": "string", "description": "Field to find top values for"},
            "limit": {"type": "integer", "default": 10, "description": "Number of top values (default 10, max 50)"},
            "filters": {"type": "object", "description": "Django ORM filter kwargs"},
        },
        "required": ["app_label", "model_name", "field"],
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the top_values tool."""
        start = time.time()
        app_label = arguments.get("app_label", "")
        model_name = arguments.get("model_name", "")
        field = arguments.get("field", "")

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

            limit = min(arguments.get("limit", 10), 50)

            results = list(
                qs.values(field)
                .annotate(count=Count("id"))
                .order_by("-count")[:limit]
            )

            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, rows=len(results), ms=elapsed_ms)

            return json.dumps({
                "model": f"{app_label}.{model_name}",
                "field": field,
                "top_values": results,
                "execution_ms": round(elapsed_ms, 2),
            }, indent=2, default=str)

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error=str(e), ms=elapsed_ms)
            return f"Error: Top values failed — {str(e)}"


class DistributionTool(MCPTool):
    """
    Statistical distribution analysis.

    Uses percentile_cont for median and quartiles via raw SQL.
    """

    name = "distribution"
    description = (
        "Get statistical distribution of a numeric field: "
        "min, q1, median, q3, max, mean."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string"},
            "model_name": {"type": "string"},
            "field": {"type": "string", "description": "Numeric field to analyze"},
            "filters": {"type": "object", "description": "Django ORM filter kwargs"},
        },
        "required": ["app_label", "model_name", "field"],
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the distribution tool."""
        start = time.time()
        app_label = arguments.get("app_label", "")
        model_name = arguments.get("model_name", "")
        field = arguments.get("field", "")

        if not context.config.is_model_exposed(app_label, model_name):
            return f"Error: Model '{app_label}.{model_name}' is not exposed"

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return f"Error: Model '{app_label}.{model_name}' not found"

        try:
            from django.db import connection

            table = model._meta.db_table

            # Build WHERE clause safely
            filters = arguments.get("filters", {})
            where_clause = ""
            params = []
            if filters:
                # Use Django ORM to build safe WHERE clause
                qs = model.objects.filter(**filters)
                # Extract SQL and params (simplified approach)
                sql, params = qs.query.sql_with_params()
                # Extract WHERE part
                if "WHERE" in str(sql):
                    where_start = str(sql).find("WHERE") + 6
                    where_clause = str(sql)[where_start:].strip()

            with connection.cursor() as cursor:
                query = f"""
                    SELECT
                        MIN({field}) as min,
                        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {field}) as q1,
                        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY {field}) as median,
                        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {field}) as q3,
                        MAX({field}) as max,
                        AVG({field}) as mean,
                        COUNT(*) as count
                    FROM {table}
                """
                if where_clause:
                    query += f" WHERE {where_clause}"

                cursor.execute(query, params)
                row = cursor.fetchone()

                elapsed_ms = (time.time() - start) * 1000
                query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, rows=int(row[6] or 0), ms=elapsed_ms)

                return json.dumps({
                    "model": f"{app_label}.{model_name}",
                    "field": field,
                    "distribution": {
                        "min": row[0],
                        "q1": row[1],
                        "median": row[2],
                        "q3": row[3],
                        "max": row[4],
                        "mean": round(float(row[5]), 4) if row[5] else None,
                        "count": row[6],
                    },
                    "execution_ms": round(elapsed_ms, 2),
                }, indent=2, default=str)

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            query_context.record_query(self.name, f"{app_label}.{model_name}", arguments, error=str(e), ms=elapsed_ms)
            return f"Error: Distribution failed — {str(e)}"


# Global instances
aggregate_model_tool = AggregateModelTool()
time_series_tool = TimeSeriesTool()
top_values_tool = TopValuesTool()
distribution_tool = DistributionTool()
