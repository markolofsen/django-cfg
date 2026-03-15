"""
High-level Admin API Client.

Provides unified access to CFG API with automatic authentication
from Streamlit session state. Uses synchronous client for Streamlit compatibility.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .config import get_base_url
from .auth import get_token, refresh_token as do_refresh_token

if TYPE_CHECKING:
    from .generated.cfg.sync_client import SyncAPIClient


class AdminAPI:
    """
    Unified Admin API Client with auto-authentication.

    Automatically retrieves JWT token from Streamlit session state
    and injects it into API calls. Uses synchronous HTTP client.

    Example:
        from api import AdminAPI, require_auth

        user = require_auth()
        api = AdminAPI()

        # Get user profile
        profile = api.cfg_user_profile.accounts_profile_retrieve()

        # List RQ queues
        queues = api.cfg_rq_queues.rq_queues_list()

        # Or use context manager
        with AdminAPI() as api:
            profile = api.cfg_user_profile.accounts_profile_retrieve()
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
    ):
        """
        Initialize AdminAPI.

        Args:
            base_url: Django API base URL (auto-detected if not provided)
            token: JWT token (auto-retrieved from session if not provided)
        """
        self._base_url = base_url or get_base_url()
        self._token = token
        self._api: "SyncAPIClient | None" = None

    @property
    def token(self) -> str | None:
        """Get current token (from provided or session)."""
        if self._token:
            return self._token
        return get_token()

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    def _ensure_api(self) -> "SyncAPIClient":
        """Get or create API instance with current token."""
        if self._api is None:
            from .generated.cfg.sync_client import SyncAPIClient

            self._api = SyncAPIClient(base_url=self._base_url)

            if token := self.token:
                self._api.set_token(token)

        return self._api

    def refresh_token(self) -> bool:
        """
        Refresh JWT token and recreate API client with new token.

        Returns:
            True if refresh succeeded
        """
        new_token = do_refresh_token()
        if new_token:
            # Force recreate client with new token
            if self._api:
                self._api.close()
            self._api = None
            self._token = new_token
            return True
        return False

    # Proxy all attribute access to underlying API
    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to CFG API."""
        return getattr(self._ensure_api(), name)

    # Context manager support (sync)
    def __enter__(self) -> "SyncAPIClient":
        """Sync context manager entry."""
        return self._ensure_api()

    def __exit__(self, *args: Any) -> None:
        """Sync context manager exit."""
        if self._api:
            self._api.close()
            self._api = None

    def close(self) -> None:
        """Close HTTP client."""
        if self._api:
            self._api.close()
            self._api = None
