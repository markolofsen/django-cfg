"""
Django CFG API - API Client with JWT Management

Usage:
    >>> from api import API
    >>>
    >>> api = API('https://api.example.com')
    >>>
    >>> # Set JWT token
    >>> api.set_token('your-jwt-token', 'refresh-token')
    >>>
    >>> # Use API
    >>> async with api:
    ...     posts = await api.posts.list()
    ...     user = await api.users.retrieve(1)
    >>>
    >>> # Check authentication
    >>> if api.is_authenticated():
    ...     # ...
    >>>
    >>> # Get OpenAPI schema
    >>> schema = api.get_schema()
"""

from __future__ import annotations

import threading
from typing import Any

import httpx

from .client import APIClient
from .schema import OPENAPI_SCHEMA
from .logger import LoggerConfig
from .retry import RetryConfig
from .cfg__accounts__auth import CfgAuthAPI
from .cfg__newsletter__bulk_email import CfgBulkEmailAPI
from .cfg__newsletter__campaigns import CfgCampaignsAPI
from .cfg__centrifugo__centrifugo_admin_api import CfgCentrifugoAdminApiAPI
from .cfg__centrifugo__centrifugo_monitoring import CfgCentrifugoMonitoringAPI
from .cfg__centrifugo__centrifugo_testing import CfgCentrifugoTestingAPI
from .cfg__dashboard__dashboard_api_zones import CfgDashboardApiZonesAPI
from .cfg__dashboard__dashboard_activity import CfgDashboardActivityAPI
from .cfg__dashboard__dashboard_charts import CfgDashboardChartsAPI
from .cfg__dashboard__dashboard_commands import CfgDashboardCommandsAPI
from .cfg__dashboard__dashboard_overview import CfgDashboardOverviewAPI
from .cfg__dashboard__dashboard_statistics import CfgDashboardStatisticsAPI
from .cfg__dashboard__dashboard_system import CfgDashboardSystemAPI
from .cfg__leads__lead_submission import CfgLeadSubmissionAPI
from .cfg__newsletter__logs import CfgLogsAPI
from .cfg__newsletter__newsletters import CfgNewslettersAPI
from .cfg__newsletter__subscriptions import CfgSubscriptionsAPI
from .cfg__newsletter__testing import CfgTestingAPI
from .cfg__accounts__user_profile import CfgUserProfileAPI
from .cfg__accounts import CfgAccountsAPI
from .cfg__centrifugo import CfgCentrifugoAPI
from .cfg__endpoints import CfgEndpointsAPI
from .cfg__health import CfgHealthAPI
from .cfg__knowbase import CfgKnowbaseAPI
from .cfg__leads import CfgLeadsAPI
from .cfg__newsletter import CfgNewsletterAPI
from .cfg__payments import CfgPaymentsAPI
from .cfg__support import CfgSupportAPI
from .cfg__tasks import CfgTasksAPI
from . import enums
# NOTE: Individual enum imports commented out due to invalid Python syntax with dotted names
# from .enums import ArchiveItem.content_type, ArchiveItemChunk.chunk_type, ArchiveItemChunkDetail.chunk_type, ArchiveItemChunkRequest.chunk_type, ArchiveItemDetail.content_type, ArchiveSearchRequestRequest.chunk_types.items, ArchiveSearchRequestRequest.content_types.items, ChatMessage.role, DocumentArchive.archive_type, DocumentArchive.processing_status, DocumentArchiveDetail.archive_type, DocumentArchiveDetail.processing_status, DocumentArchiveList.archive_type, DocumentArchiveList.processing_status, EmailLog.status, LeadSubmission.contact_type, LeadSubmissionRequest.contact_type, NewsletterCampaign.status, OTPRequestRequest.channel, OTPVerifyRequest.channel, PatchedArchiveItemChunkRequest.chunk_type, PatchedLeadSubmissionRequest.contact_type, PatchedTicketRequest.status, PaymentDetail.status, PaymentList.status, QueueAction.action, QueueActionRequest.action, QuickAction.color, StatCard.change_type, SystemHealth.overall_status, SystemHealthItem.status, Ticket.status, TicketRequest.status, Transaction.transaction_type, WorkerAction.action, WorkerActionRequest.action

TOKEN_KEY = "auth_token"
REFRESH_TOKEN_KEY = "refresh_token"

class API:
    """
    API Client wrapper with JWT token management.

    This class provides:
    - Thread-safe JWT token storage
    - Automatic Authorization header injection
    - Context manager support for async operations
    - Optional retry and logging configuration

    Example:
        >>> api = API('https://api.example.com')
        >>> api.set_token('jwt-token')
        >>> async with api:
        ...     users = await api.users.list()
        >>>
        >>> # With retry and logging
        >>> api = API(
        ...     'https://api.example.com',
        ...     retry_config=RetryConfig(max_attempts=5),
        ...     logger_config=LoggerConfig(enabled=True)
        ... )
    """

    def __init__(
        self,
        base_url: str,
        logger_config: LoggerConfig | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Any
    ):
        """
        Initialize API client.

        Args:
            base_url: Base API URL (e.g., 'https://api.example.com')
            logger_config: Logger configuration (None to disable logging)
            retry_config: Retry configuration (None to disable retry)
            **kwargs: Additional httpx.AsyncClient kwargs
        """
        self.base_url = base_url.rstrip('/')
        self._kwargs = kwargs
        self._logger_config = logger_config
        self._retry_config = retry_config
        self._token: str | None = None
        self._refresh_token: str | None = None
        self._lock = threading.Lock()
        self._client: APIClient | None = None
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize API client with current token."""
        # Create httpx client with auth header if token exists
        headers = {}
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'

        kwargs = {**self._kwargs}
        if headers:
            kwargs['headers'] = headers

        # Create new APIClient
        self._client = APIClient(
            self.base_url,
            logger_config=self._logger_config,
            retry_config=self._retry_config,
            **kwargs
        )

    @property
    def cfg_auth(self) -> CfgAuthAPI:
        """Access Auth endpoints."""
        return self._client.cfg_auth

    @property
    def cfg_bulk_email(self) -> CfgBulkEmailAPI:
        """Access Bulk Email endpoints."""
        return self._client.cfg_bulk_email

    @property
    def cfg_campaigns(self) -> CfgCampaignsAPI:
        """Access Campaigns endpoints."""
        return self._client.cfg_campaigns

    @property
    def cfg_centrifugo_admin_api(self) -> CfgCentrifugoAdminApiAPI:
        """Access Centrifugo Admin API endpoints."""
        return self._client.cfg_centrifugo_admin_api

    @property
    def cfg_centrifugo_monitoring(self) -> CfgCentrifugoMonitoringAPI:
        """Access Centrifugo Monitoring endpoints."""
        return self._client.cfg_centrifugo_monitoring

    @property
    def cfg_centrifugo_testing(self) -> CfgCentrifugoTestingAPI:
        """Access Centrifugo Testing endpoints."""
        return self._client.cfg_centrifugo_testing

    @property
    def cfg_dashboard_api_zones(self) -> CfgDashboardApiZonesAPI:
        """Access Dashboard - API Zones endpoints."""
        return self._client.cfg_dashboard_api_zones

    @property
    def cfg_dashboard_activity(self) -> CfgDashboardActivityAPI:
        """Access Dashboard - Activity endpoints."""
        return self._client.cfg_dashboard_activity

    @property
    def cfg_dashboard_charts(self) -> CfgDashboardChartsAPI:
        """Access Dashboard - Charts endpoints."""
        return self._client.cfg_dashboard_charts

    @property
    def cfg_dashboard_commands(self) -> CfgDashboardCommandsAPI:
        """Access Dashboard - Commands endpoints."""
        return self._client.cfg_dashboard_commands

    @property
    def cfg_dashboard_overview(self) -> CfgDashboardOverviewAPI:
        """Access Dashboard - Overview endpoints."""
        return self._client.cfg_dashboard_overview

    @property
    def cfg_dashboard_statistics(self) -> CfgDashboardStatisticsAPI:
        """Access Dashboard - Statistics endpoints."""
        return self._client.cfg_dashboard_statistics

    @property
    def cfg_dashboard_system(self) -> CfgDashboardSystemAPI:
        """Access Dashboard - System endpoints."""
        return self._client.cfg_dashboard_system

    @property
    def cfg_lead_submission(self) -> CfgLeadSubmissionAPI:
        """Access Lead Submission endpoints."""
        return self._client.cfg_lead_submission

    @property
    def cfg_logs(self) -> CfgLogsAPI:
        """Access Logs endpoints."""
        return self._client.cfg_logs

    @property
    def cfg_newsletters(self) -> CfgNewslettersAPI:
        """Access Newsletters endpoints."""
        return self._client.cfg_newsletters

    @property
    def cfg_subscriptions(self) -> CfgSubscriptionsAPI:
        """Access Subscriptions endpoints."""
        return self._client.cfg_subscriptions

    @property
    def cfg_testing(self) -> CfgTestingAPI:
        """Access Testing endpoints."""
        return self._client.cfg_testing

    @property
    def cfg_user_profile(self) -> CfgUserProfileAPI:
        """Access User Profile endpoints."""
        return self._client.cfg_user_profile

    @property
    def cfg_accounts(self) -> CfgAccountsAPI:
        """Access accounts endpoints."""
        return self._client.cfg_accounts

    @property
    def cfg_centrifugo(self) -> CfgCentrifugoAPI:
        """Access centrifugo endpoints."""
        return self._client.cfg_centrifugo

    @property
    def cfg_endpoints(self) -> CfgEndpointsAPI:
        """Access endpoints endpoints."""
        return self._client.cfg_endpoints

    @property
    def cfg_health(self) -> CfgHealthAPI:
        """Access health endpoints."""
        return self._client.cfg_health

    @property
    def cfg_knowbase(self) -> CfgKnowbaseAPI:
        """Access knowbase endpoints."""
        return self._client.cfg_knowbase

    @property
    def cfg_leads(self) -> CfgLeadsAPI:
        """Access leads endpoints."""
        return self._client.cfg_leads

    @property
    def cfg_newsletter(self) -> CfgNewsletterAPI:
        """Access newsletter endpoints."""
        return self._client.cfg_newsletter

    @property
    def cfg_payments(self) -> CfgPaymentsAPI:
        """Access payments endpoints."""
        return self._client.cfg_payments

    @property
    def cfg_support(self) -> CfgSupportAPI:
        """Access support endpoints."""
        return self._client.cfg_support

    @property
    def cfg_tasks(self) -> CfgTasksAPI:
        """Access tasks endpoints."""
        return self._client.cfg_tasks

    def get_token(self) -> str | None:
        """Get current JWT token."""
        with self._lock:
            return self._token

    def get_refresh_token(self) -> str | None:
        """Get current refresh token."""
        with self._lock:
            return self._refresh_token

    def set_token(self, token: str, refresh_token: str | None = None) -> None:
        """
        Set JWT token and refresh token.

        Args:
            token: JWT access token
            refresh_token: JWT refresh token (optional)
        """
        with self._lock:
            self._token = token
            if refresh_token:
                self._refresh_token = refresh_token

        # Reinitialize clients with new token
        self._init_clients()

    def clear_tokens(self) -> None:
        """Clear all tokens."""
        with self._lock:
            self._token = None
            self._refresh_token = None

        # Reinitialize clients without token
        self._init_clients()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.get_token() is not None

    def set_base_url(self, url: str) -> None:
        """
        Update base URL and reinitialize clients.

        Args:
            url: New base URL
        """
        self.base_url = url.rstrip('/')
        self._init_clients()

    def get_base_url(self) -> str:
        """Get current base URL."""
        return self.base_url

    def get_schema(self) -> dict[str, Any]:
        """
        Get OpenAPI schema.

        Returns:
            Complete OpenAPI specification for this API
        """
        return OPENAPI_SCHEMA

    async def __aenter__(self) -> 'API':
        """Async context manager entry."""
        if self._client:
            await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.close()

__all__ = [
    "API",
    "APIClient",
]