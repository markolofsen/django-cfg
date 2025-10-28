from __future__ import annotations

from typing import Any, Optional

import httpx

from .cfg__accounts__auth.sync_client import SyncCfgAuthAPI
from .cfg__newsletter__bulk_email.sync_client import SyncCfgBulkEmailAPI
from .cfg__newsletter__campaigns.sync_client import SyncCfgCampaignsAPI
from .cfg__centrifugo__centrifugo_admin_api.sync_client import SyncCfgCentrifugoAdminApiAPI
from .cfg__centrifugo__centrifugo_monitoring.sync_client import SyncCfgCentrifugoMonitoringAPI
from .cfg__centrifugo__centrifugo_testing.sync_client import SyncCfgCentrifugoTestingAPI
from .cfg__dashboard__dashboard_api_zones.sync_client import SyncCfgDashboardApiZonesAPI
from .cfg__dashboard__dashboard_activity.sync_client import SyncCfgDashboardActivityAPI
from .cfg__dashboard__dashboard_charts.sync_client import SyncCfgDashboardChartsAPI
from .cfg__dashboard__dashboard_commands.sync_client import SyncCfgDashboardCommandsAPI
from .cfg__dashboard__dashboard_overview.sync_client import SyncCfgDashboardOverviewAPI
from .cfg__dashboard__dashboard_statistics.sync_client import SyncCfgDashboardStatisticsAPI
from .cfg__dashboard__dashboard_system.sync_client import SyncCfgDashboardSystemAPI
from .cfg__leads__lead_submission.sync_client import SyncCfgLeadSubmissionAPI
from .cfg__newsletter__logs.sync_client import SyncCfgLogsAPI
from .cfg__newsletter__newsletters.sync_client import SyncCfgNewslettersAPI
from .cfg__newsletter__subscriptions.sync_client import SyncCfgSubscriptionsAPI
from .cfg__newsletter__testing.sync_client import SyncCfgTestingAPI
from .cfg__accounts__user_profile.sync_client import SyncCfgUserProfileAPI
from .cfg__accounts.sync_client import SyncCfgAccountsAPI
from .cfg__centrifugo.sync_client import SyncCfgCentrifugoAPI
from .cfg__endpoints.sync_client import SyncCfgEndpointsAPI
from .cfg__health.sync_client import SyncCfgHealthAPI
from .cfg__knowbase.sync_client import SyncCfgKnowbaseAPI
from .cfg__leads.sync_client import SyncCfgLeadsAPI
from .cfg__newsletter.sync_client import SyncCfgNewsletterAPI
from .cfg__payments.sync_client import SyncCfgPaymentsAPI
from .cfg__support.sync_client import SyncCfgSupportAPI
from .cfg__tasks.sync_client import SyncCfgTasksAPI
from .logger import APILogger, LoggerConfig
from .retry import RetryConfig, RetryAsyncClient


class SyncAPIClient:
    """
    Synchronous API client for Django CFG API.

    Usage:
        >>> with SyncAPIClient(base_url='https://api.example.com') as client:
        ...     users = client.users.list()
        ...     post = client.posts.create(data=new_post)
    """

    def __init__(
        self,
        base_url: str,
        logger_config: Optional[LoggerConfig] = None,
        **kwargs: Any,
    ):
        """
        Initialize sync API client.

        Args:
            base_url: Base API URL (e.g., 'https://api.example.com')
            logger_config: Logger configuration (None to disable logging)
            **kwargs: Additional httpx.Client kwargs
        """
        self.base_url = base_url.rstrip('/')
        self._client = httpx.Client(
            base_url=self.base_url,
            **kwargs,
        )

        # Initialize logger
        self.logger: Optional[APILogger] = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.cfg_auth = SyncCfgAuthAPI(self._client)
        self.cfg_bulk_email = SyncCfgBulkEmailAPI(self._client)
        self.cfg_campaigns = SyncCfgCampaignsAPI(self._client)
        self.cfg_centrifugo_admin_api = SyncCfgCentrifugoAdminApiAPI(self._client)
        self.cfg_centrifugo_monitoring = SyncCfgCentrifugoMonitoringAPI(self._client)
        self.cfg_centrifugo_testing = SyncCfgCentrifugoTestingAPI(self._client)
        self.cfg_dashboard_api_zones = SyncCfgDashboardApiZonesAPI(self._client)
        self.cfg_dashboard_activity = SyncCfgDashboardActivityAPI(self._client)
        self.cfg_dashboard_charts = SyncCfgDashboardChartsAPI(self._client)
        self.cfg_dashboard_commands = SyncCfgDashboardCommandsAPI(self._client)
        self.cfg_dashboard_overview = SyncCfgDashboardOverviewAPI(self._client)
        self.cfg_dashboard_statistics = SyncCfgDashboardStatisticsAPI(self._client)
        self.cfg_dashboard_system = SyncCfgDashboardSystemAPI(self._client)
        self.cfg_lead_submission = SyncCfgLeadSubmissionAPI(self._client)
        self.cfg_logs = SyncCfgLogsAPI(self._client)
        self.cfg_newsletters = SyncCfgNewslettersAPI(self._client)
        self.cfg_subscriptions = SyncCfgSubscriptionsAPI(self._client)
        self.cfg_testing = SyncCfgTestingAPI(self._client)
        self.cfg_user_profile = SyncCfgUserProfileAPI(self._client)
        self.cfg_accounts = SyncCfgAccountsAPI(self._client)
        self.cfg_centrifugo = SyncCfgCentrifugoAPI(self._client)
        self.cfg_endpoints = SyncCfgEndpointsAPI(self._client)
        self.cfg_health = SyncCfgHealthAPI(self._client)
        self.cfg_knowbase = SyncCfgKnowbaseAPI(self._client)
        self.cfg_leads = SyncCfgLeadsAPI(self._client)
        self.cfg_newsletter = SyncCfgNewsletterAPI(self._client)
        self.cfg_payments = SyncCfgPaymentsAPI(self._client)
        self.cfg_support = SyncCfgSupportAPI(self._client)
        self.cfg_tasks = SyncCfgTasksAPI(self._client)

    def __enter__(self) -> 'SyncAPIClient':
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.close()

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()