from __future__ import annotations

from typing import Any, Optional

import httpx

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
from .logger import APILogger, LoggerConfig
from .retry import RetryConfig, RetryAsyncClient


class APIClient:
    """
    Async API client for Django CFG API.

    Usage:
        >>> async with APIClient(base_url='https://api.example.com') as client:
        ...     users = await client.users.list()
        ...     post = await client.posts.create(data=new_post)
        >>>
        >>> # With retry configuration
        >>> retry_config = RetryConfig(max_attempts=5, min_wait=2.0)
        >>> async with APIClient(base_url='https://api.example.com', retry_config=retry_config) as client:
        ...     users = await client.users.list()
    """

    def __init__(
        self,
        base_url: str,
        logger_config: Optional[LoggerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        **kwargs: Any,
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

        # Create HTTP client with or without retry
        if retry_config is not None:
            self._client = RetryAsyncClient(
                base_url=self.base_url,
                retry_config=retry_config,
                **kwargs,
            )
        else:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                **kwargs,
            )

        # Initialize logger
        self.logger: Optional[APILogger] = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.cfg_auth = CfgAuthAPI(self._client)
        self.cfg_bulk_email = CfgBulkEmailAPI(self._client)
        self.cfg_campaigns = CfgCampaignsAPI(self._client)
        self.cfg_centrifugo_admin_api = CfgCentrifugoAdminApiAPI(self._client)
        self.cfg_centrifugo_monitoring = CfgCentrifugoMonitoringAPI(self._client)
        self.cfg_centrifugo_testing = CfgCentrifugoTestingAPI(self._client)
        self.cfg_dashboard_api_zones = CfgDashboardApiZonesAPI(self._client)
        self.cfg_dashboard_activity = CfgDashboardActivityAPI(self._client)
        self.cfg_dashboard_charts = CfgDashboardChartsAPI(self._client)
        self.cfg_dashboard_commands = CfgDashboardCommandsAPI(self._client)
        self.cfg_dashboard_overview = CfgDashboardOverviewAPI(self._client)
        self.cfg_dashboard_statistics = CfgDashboardStatisticsAPI(self._client)
        self.cfg_dashboard_system = CfgDashboardSystemAPI(self._client)
        self.cfg_lead_submission = CfgLeadSubmissionAPI(self._client)
        self.cfg_logs = CfgLogsAPI(self._client)
        self.cfg_newsletters = CfgNewslettersAPI(self._client)
        self.cfg_subscriptions = CfgSubscriptionsAPI(self._client)
        self.cfg_testing = CfgTestingAPI(self._client)
        self.cfg_user_profile = CfgUserProfileAPI(self._client)
        self.cfg_accounts = CfgAccountsAPI(self._client)
        self.cfg_centrifugo = CfgCentrifugoAPI(self._client)
        self.cfg_endpoints = CfgEndpointsAPI(self._client)
        self.cfg_health = CfgHealthAPI(self._client)
        self.cfg_knowbase = CfgKnowbaseAPI(self._client)
        self.cfg_leads = CfgLeadsAPI(self._client)
        self.cfg_newsletter = CfgNewsletterAPI(self._client)
        self.cfg_payments = CfgPaymentsAPI(self._client)
        self.cfg_support = CfgSupportAPI(self._client)
        self.cfg_tasks = CfgTasksAPI(self._client)

    async def __aenter__(self) -> 'APIClient':
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()