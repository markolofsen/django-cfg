from __future__ import annotations

from typing import Any

import httpx

from .helpers import APILogger, LoggerConfig, RetryAsyncClient, RetryConfig
from .cfg__accounts__auth import CfgAuthAPI
from .cfg__totp__backup_codes import CfgBackupCodesAPI
from .cfg__centrifugo__centrifugo_admin_api import CfgCentrifugoAdminApiAPI
from .cfg__centrifugo__centrifugo_auth import CfgCentrifugoAuthAPI
from .cfg__centrifugo__centrifugo_monitoring import CfgCentrifugoMonitoringAPI
from .cfg__centrifugo__centrifugo_testing import CfgCentrifugoTestingAPI
from .cfg__dashboard__dashboard_api_zones import CfgDashboardApiZonesAPI
from .cfg__dashboard__dashboard_activity import CfgDashboardActivityAPI
from .cfg__dashboard__dashboard_charts import CfgDashboardChartsAPI
from .cfg__dashboard__dashboard_commands import CfgDashboardCommandsAPI
from .cfg__dashboard__dashboard_config import CfgDashboardConfigAPI
from .cfg__dashboard__dashboard_overview import CfgDashboardOverviewAPI
from .cfg__dashboard__dashboard_statistics import CfgDashboardStatisticsAPI
from .cfg__dashboard__dashboard_system import CfgDashboardSystemAPI
from .cfg__dashboard__dashboard_metrics import CfgDashboardMetricsAPI
from .cfg__accounts__oauth import CfgOauthAPI
from .cfg__rq__rq_jobs import CfgRqJobsAPI
from .cfg__rq__rq_monitoring import CfgRqMonitoringAPI
from .cfg__rq__rq_queues import CfgRqQueuesAPI
from .cfg__rq__rq_registries import CfgRqRegistriesAPI
from .cfg__rq__rq_schedules import CfgRqSchedulesAPI
from .cfg__rq__rq_testing import CfgRqTestingAPI
from .cfg__rq__rq_workers import CfgRqWorkersAPI
from .cfg__totp__totp_management import CfgTotpManagementAPI
from .cfg__totp__totp_setup import CfgTotpSetupAPI
from .cfg__totp__totp_verification import CfgTotpVerificationAPI
from .cfg__accounts__user_profile import CfgUserProfileAPI
from .cfg__accounts import CfgAccountsAPI
from .cfg__grpc__grpc_api_keys import CfgGrpcApiKeysAPI
from .cfg__grpc__grpc_configuration import CfgGrpcConfigurationAPI
from .cfg__grpc__grpc_monitoring import CfgGrpcMonitoringAPI
from .cfg__grpc__grpc_services import CfgGrpcServicesAPI
from .cfg__health import CfgHealthAPI
from .cfg__totp import CfgTotpAPI


class APIClient:
    """
    Async API client for Django CFG API.

    Usage:
        >>> async with APIClient(base_url='https://api.example.com') as client:
        ...     users = await client.users.list()
        ...     post = await client.posts.create(data=new_post)
        >>>
        >>> # With retry configuration
        >>> retry = RetryConfig(max_attempts=5, min_wait=2.0)
        >>> async with APIClient('https://api.example.com', retry_config=retry) as c:
        ...     users = await c.users.list()
    """

    def __init__(
        self,
        base_url: str,
        logger_config: LoggerConfig | None = None,
        retry_config: RetryConfig | None = None,
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
        self.logger: APILogger | None = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.cfg_auth = CfgAuthAPI(self._client)
        self.cfg_backup_codes = CfgBackupCodesAPI(self._client)
        self.cfg_centrifugo_admin_api = CfgCentrifugoAdminApiAPI(self._client)
        self.cfg_centrifugo_auth = CfgCentrifugoAuthAPI(self._client)
        self.cfg_centrifugo_monitoring = CfgCentrifugoMonitoringAPI(self._client)
        self.cfg_centrifugo_testing = CfgCentrifugoTestingAPI(self._client)
        self.cfg_dashboard_api_zones = CfgDashboardApiZonesAPI(self._client)
        self.cfg_dashboard_activity = CfgDashboardActivityAPI(self._client)
        self.cfg_dashboard_charts = CfgDashboardChartsAPI(self._client)
        self.cfg_dashboard_commands = CfgDashboardCommandsAPI(self._client)
        self.cfg_dashboard_config = CfgDashboardConfigAPI(self._client)
        self.cfg_dashboard_overview = CfgDashboardOverviewAPI(self._client)
        self.cfg_dashboard_statistics = CfgDashboardStatisticsAPI(self._client)
        self.cfg_dashboard_system = CfgDashboardSystemAPI(self._client)
        self.cfg_dashboard_metrics = CfgDashboardMetricsAPI(self._client)
        self.cfg_oauth = CfgOauthAPI(self._client)
        self.cfg_rq_jobs = CfgRqJobsAPI(self._client)
        self.cfg_rq_monitoring = CfgRqMonitoringAPI(self._client)
        self.cfg_rq_queues = CfgRqQueuesAPI(self._client)
        self.cfg_rq_registries = CfgRqRegistriesAPI(self._client)
        self.cfg_rq_schedules = CfgRqSchedulesAPI(self._client)
        self.cfg_rq_testing = CfgRqTestingAPI(self._client)
        self.cfg_rq_workers = CfgRqWorkersAPI(self._client)
        self.cfg_totp_management = CfgTotpManagementAPI(self._client)
        self.cfg_totp_setup = CfgTotpSetupAPI(self._client)
        self.cfg_totp_verification = CfgTotpVerificationAPI(self._client)
        self.cfg_user_profile = CfgUserProfileAPI(self._client)
        self.cfg_accounts = CfgAccountsAPI(self._client)
        self.cfg_grpc_api_keys = CfgGrpcApiKeysAPI(self._client)
        self.cfg_grpc_configuration = CfgGrpcConfigurationAPI(self._client)
        self.cfg_grpc_monitoring = CfgGrpcMonitoringAPI(self._client)
        self.cfg_grpc_services = CfgGrpcServicesAPI(self._client)
        self.cfg_health = CfgHealthAPI(self._client)
        self.cfg_totp = CfgTotpAPI(self._client)

    async def __aenter__(self) -> APIClient:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()