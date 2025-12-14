"""
Metrics Service

Universal metrics collection service supporting multiple metric categories:
- LLM provider balances
- System health
- API usage statistics
- Database metrics
- Custom metrics

Extensible architecture allows easy addition of new metric categories.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Universal metrics collection service.

    %%PRIORITY:HIGH%%
    %%AI_HINT: Collects metrics from various sources in unified format%%

    TAGS: metrics, monitoring, dashboard, api
    DEPENDS_ON: [django_llm_monitoring, django.core.cache]
    """

    def __init__(self):
        """Initialize metrics service."""
        self.logger = logger

    def get_all_metrics(
        self,
        categories: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get all metrics or specific categories.

        Args:
            categories: List of category names to fetch (None = all)
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            Dict with metrics organized by category:
                {
                    "categories": {
                        "llm_balances": {...},
                        "system_health": {...}
                    },
                    "metadata": {
                        "timestamp": "...",
                        "categories_count": 2
                    }
                }
        """
        # Available metric categories
        available_categories = {
            "llm_balances": self._get_llm_balances,
            "system_health": self._get_system_health,
            "api_stats": self._get_api_stats,
        }

        # Determine which categories to fetch
        if categories:
            selected = {
                cat: func
                for cat, func in available_categories.items()
                if cat in categories
            }
        else:
            selected = available_categories

        # Collect metrics
        result = {"categories": {}, "metadata": {}}

        for category_name, fetch_func in selected.items():
            try:
                result["categories"][category_name] = fetch_func(force_refresh)
            except Exception as e:
                self.logger.exception(f"Failed to fetch {category_name} metrics: {e}")
                result["categories"][category_name] = {
                    "name": category_name,
                    "status": "error",
                    "error": str(e),
                    "items": []
                }

        # Add metadata
        result["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "categories_count": len(result["categories"]),
            "categories_requested": categories or list(available_categories.keys()),
        }

        return result

    def _get_llm_balances(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get LLM provider balances.

        Args:
            force_refresh: Bypass cache

        Returns:
            Category data with provider balances
        """
        try:
            from django_cfg.modules.django_llm_monitoring import BalanceChecker

            checker = BalanceChecker()
            balances = checker.check_all_balances(force=force_refresh)

            # Transform to dashboard format
            items = []
            overall_status = "ok"

            for provider_name, balance_data in balances.items():
                item = {
                    "provider": provider_name,
                    "provider_display": provider_name.replace("_", " ").title(),
                    "balance": balance_data.balance,
                    "currency": balance_data.currency,
                    "usage": balance_data.usage,
                    "limit": balance_data.limit,
                    "status": balance_data.status,
                    "note": balance_data.note,
                    "error": balance_data.error,
                }

                # Determine item status
                if balance_data.error:
                    item["status_level"] = "error"
                    overall_status = "error"
                elif balance_data.balance is None:
                    # No balance available - check API key status
                    item["status_level"] = "info" if balance_data.status == "valid" else "warning"
                elif balance_data.balance <= 5.0:
                    item["status_level"] = "critical"
                    if overall_status != "error":
                        overall_status = "critical"
                elif balance_data.balance <= 10.0:
                    item["status_level"] = "warning"
                    if overall_status not in ["error", "critical"]:
                        overall_status = "warning"
                else:
                    item["status_level"] = "ok"

                items.append(item)

            return {
                "name": "LLM Provider Balances",
                "description": "API key status and account balances for LLM providers",
                "status": overall_status,
                "items": items,
                "summary": {
                    "total_providers": len(items),
                    "total_balance": sum(
                        item["balance"] for item in items
                        if item["balance"] is not None
                    ),
                    "providers_with_errors": sum(
                        1 for item in items
                        if item.get("error")
                    ),
                    "providers_critical": sum(
                        1 for item in items
                        if item.get("status_level") == "critical"
                    ),
                }
            }

        except Exception as e:
            self.logger.exception(f"Failed to get LLM balances: {e}")
            return {
                "name": "LLM Provider Balances",
                "status": "error",
                "error": str(e),
                "items": []
            }

    def _get_system_health(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get system health metrics.

        Args:
            force_refresh: Bypass cache

        Returns:
            Category data with system health
        """
        try:
            from .system_health_service import SystemHealthService

            health_service = SystemHealthService()

            # Collect health checks
            items = [
                health_service.check_database_health(),
                health_service.check_cache_health(),
            ]

            # Try queue health if RQ is available
            try:
                items.append(health_service.check_queue_health())
            except AttributeError:
                pass

            # Calculate overall status
            statuses = [item.get("status") for item in items]
            if "error" in statuses:
                overall_status = "error"
            elif "warning" in statuses:
                overall_status = "warning"
            else:
                overall_status = "ok"

            return {
                "name": "System Health",
                "description": "Health status of system components",
                "status": overall_status,
                "items": items,
                "summary": {
                    "total_components": len(items),
                    "healthy": sum(1 for item in items if item.get("status") == "healthy"),
                    "warnings": sum(1 for item in items if item.get("status") == "warning"),
                    "errors": sum(1 for item in items if item.get("status") == "error"),
                }
            }

        except Exception as e:
            self.logger.exception(f"Failed to get system health: {e}")
            return {
                "name": "System Health",
                "status": "error",
                "error": str(e),
                "items": []
            }

    def _get_api_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get API usage statistics.

        Args:
            force_refresh: Bypass cache

        Returns:
            Category data with API stats
        """
        # Placeholder for API stats
        # TODO: Implement when API usage tracking is available
        return {
            "name": "API Usage Statistics",
            "description": "API request statistics and rate limits",
            "status": "unavailable",
            "note": "API usage tracking not yet implemented",
            "items": []
        }
