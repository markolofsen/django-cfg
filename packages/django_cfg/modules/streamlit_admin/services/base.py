"""Base service class for Streamlit admin.

Provides API client injection, error handling, and common utilities.
"""

from __future__ import annotations

import logging
import traceback
from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from api import AdminAPI

R = TypeVar("R")

logger = logging.getLogger(__name__)


def log_api_error(operation: str, exc: Exception) -> None:
    """Log API error with full traceback."""
    tb = traceback.format_exc()
    logger.error(f"API error in {operation}: {exc}\n{tb}")


class BaseService:
    """Base service with API client injection.

    Usage:
        class DashboardService(BaseService):
            def get_stats(self) -> list[StatCard]:
                data = self.api.cfg_overview.retrieve()
                return [StatCard.model_validate(c) for c in data.stat_cards]
    """

    __slots__ = ("_api",)

    def __init__(self, api: "AdminAPI | None" = None) -> None:
        """Initialize service with optional API client.

        Args:
            api: AdminAPI instance. Creates new one if not provided.
        """
        self._api = api

    @property
    def api(self) -> "AdminAPI":
        """Get API client (lazy initialization)."""
        if self._api is None:
            from api import AdminAPI

            self._api = AdminAPI()
        return self._api

    def _safe_call(
        self,
        operation: str,
        call: Callable[[], R],
        default: R,
    ) -> R:
        """Execute API call with error logging and default fallback.

        Args:
            operation: Name of the operation for logging.
            call: Callable that performs the API call.
            default: Default value to return on error.

        Returns:
            Result of the call or default on error.
        """
        try:
            return call()
        except Exception as exc:
            log_api_error(operation, exc)
            return default
