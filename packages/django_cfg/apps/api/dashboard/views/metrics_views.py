"""
Metrics Views

Universal metrics API endpoints.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ..serializers.metrics import MetricsResponseSerializer
from ..services.metrics_service import MetricsService


class MetricsViewSet(viewsets.ViewSet):
    """
    Universal metrics API.

    Provides metrics from multiple categories:
    - LLM provider balances
    - System health
    - API usage statistics
    - Custom metrics

    %%PRIORITY:HIGH%%
    %%AI_HINT: Universal metrics endpoint for dashboard%%

    TAGS: metrics, api, dashboard
    """

    @extend_schema(
        summary="Get all metrics",
        description=(
            "Retrieve metrics from all or specific categories.\n\n"
            "**Available Categories:**\n"
            "- `llm_balances` - LLM provider API keys and account balances\n"
            "- `system_health` - Database, cache, queue health status\n"
            "- `api_stats` - API usage statistics (coming soon)\n\n"
            "**Query Parameters:**\n"
            "- `categories` - Comma-separated list of categories (optional)\n"
            "- `force` - Force refresh, bypass cache (default: false)"
        ),
        parameters=[
            OpenApiParameter(
                name="categories",
                description="Comma-separated metric categories (e.g., 'llm_balances,system_health')",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="force",
                description="Force refresh data (bypass cache)",
                required=False,
                type=bool,
            ),
        ],
        responses={200: MetricsResponseSerializer},
        tags=["Dashboard Metrics"]
    )
    def list(self, request):
        """
        Get all metrics or specific categories.

        Query params:
            categories: Comma-separated list (e.g., "llm_balances,system_health")
            force: Boolean to force refresh

        Returns:
            Metrics organized by category

        Example:
            GET /api/dashboard/api/metrics/
            GET /api/dashboard/api/metrics/?categories=llm_balances
            GET /api/dashboard/api/metrics/?force=true
        """
        # Parse query parameters
        categories_param = request.query_params.get("categories")
        force_refresh = request.query_params.get("force", "false").lower() == "true"

        # Parse categories
        categories = None
        if categories_param:
            categories = [cat.strip() for cat in categories_param.split(",")]

        # Fetch metrics
        service = MetricsService()
        data = service.get_all_metrics(
            categories=categories,
            force_refresh=force_refresh
        )

        # Serialize and return
        serializer = MetricsResponseSerializer(data)
        return Response(serializer.data)

    @extend_schema(
        summary="Get LLM balances",
        description=(
            "Get LLM provider balances and API key status.\n\n"
            "**Providers:**\n"
            "- OpenAI - API key validation (balance check unavailable)\n"
            "- OpenRouter - Prepaid credit balance\n\n"
            "**Status Levels:**\n"
            "- `ok` - Balance above $10 or API key valid\n"
            "- `warning` - Balance between $5-$10\n"
            "- `critical` - Balance below $5\n"
            "- `error` - API key invalid or request failed"
        ),
        parameters=[
            OpenApiParameter(
                name="force",
                description="Force refresh data (bypass cache)",
                required=False,
                type=bool,
            ),
        ],
        tags=["Dashboard Metrics"]
    )
    @action(detail=False, methods=["get"], url_path="llm-balances")
    def llm_balances(self, request):
        """
        Get LLM provider balances.

        Shortcut endpoint for LLM balances category.

        Query params:
            force: Boolean to force refresh

        Returns:
            LLM balances category data

        Example:
            GET /api/dashboard/api/metrics/llm-balances/
            GET /api/dashboard/api/metrics/llm-balances/?force=true
        """
        force_refresh = request.query_params.get("force", "false").lower() == "true"

        service = MetricsService()
        data = service.get_all_metrics(
            categories=["llm_balances"],
            force_refresh=force_refresh
        )

        return Response(data["categories"]["llm_balances"])

    @extend_schema(
        summary="Get system health",
        description=(
            "Get system component health status.\n\n"
            "**Components:**\n"
            "- Database - PostgreSQL/MySQL connectivity\n"
            "- Cache - Redis/Memcached status\n"
            "- Queue - RQ/Celery worker status (if available)"
        ),
        parameters=[
            OpenApiParameter(
                name="force",
                description="Force refresh data (bypass cache)",
                required=False,
                type=bool,
            ),
        ],
        tags=["Dashboard Metrics"]
    )
    @action(detail=False, methods=["get"], url_path="system-health")
    def system_health(self, request):
        """
        Get system health status.

        Shortcut endpoint for system health category.

        Query params:
            force: Boolean to force refresh

        Returns:
            System health category data

        Example:
            GET /api/dashboard/api/metrics/system-health/
        """
        force_refresh = request.query_params.get("force", "false").lower() == "true"

        service = MetricsService()
        data = service.get_all_metrics(
            categories=["system_health"],
            force_refresh=force_refresh
        )

        return Response(data["categories"]["system_health"])
