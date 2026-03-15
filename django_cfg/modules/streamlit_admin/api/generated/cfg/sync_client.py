from __future__ import annotations

from typing import Any

import httpx

from .helpers import APILogger, LoggerConfig
from .cfg__accounts__auth.sync_client import SyncCfgAuthAPI
from .cfg__totp__backup_codes.sync_client import SyncCfgBackupCodesAPI
from .cfg__centrifugo__centrifugo_admin_api.sync_client import SyncCfgCentrifugoAdminApiAPI
from .cfg__centrifugo__centrifugo_auth.sync_client import SyncCfgCentrifugoAuthAPI
from .cfg__centrifugo__centrifugo_monitoring.sync_client import SyncCfgCentrifugoMonitoringAPI
from .cfg__centrifugo__centrifugo_testing.sync_client import SyncCfgCentrifugoTestingAPI
from .cfg__dashboard__dashboard_api_zones.sync_client import SyncCfgDashboardApiZonesAPI
from .cfg__dashboard__dashboard_activity.sync_client import SyncCfgDashboardActivityAPI
from .cfg__dashboard__dashboard_charts.sync_client import SyncCfgDashboardChartsAPI
from .cfg__dashboard__dashboard_commands.sync_client import SyncCfgDashboardCommandsAPI
from .cfg__dashboard__dashboard_config.sync_client import SyncCfgDashboardConfigAPI
from .cfg__dashboard__dashboard_overview.sync_client import SyncCfgDashboardOverviewAPI
from .cfg__dashboard__dashboard_statistics.sync_client import SyncCfgDashboardStatisticsAPI
from .cfg__dashboard__dashboard_system.sync_client import SyncCfgDashboardSystemAPI
from .cfg__dashboard__dashboard_metrics.sync_client import SyncCfgDashboardMetricsAPI
from .cfg__accounts__oauth.sync_client import SyncCfgOauthAPI
from .cfg__rq__rq_jobs.sync_client import SyncCfgRqJobsAPI
from .cfg__rq__rq_monitoring.sync_client import SyncCfgRqMonitoringAPI
from .cfg__rq__rq_queues.sync_client import SyncCfgRqQueuesAPI
from .cfg__rq__rq_registries.sync_client import SyncCfgRqRegistriesAPI
from .cfg__rq__rq_schedules.sync_client import SyncCfgRqSchedulesAPI
from .cfg__rq__rq_testing.sync_client import SyncCfgRqTestingAPI
from .cfg__rq__rq_workers.sync_client import SyncCfgRqWorkersAPI
from .cfg__totp__totp_management.sync_client import SyncCfgTotpManagementAPI
from .cfg__totp__totp_setup.sync_client import SyncCfgTotpSetupAPI
from .cfg__totp__totp_verification.sync_client import SyncCfgTotpVerificationAPI
from .cfg__accounts__user_profile.sync_client import SyncCfgUserProfileAPI
from .cfg__accounts.sync_client import SyncCfgAccountsAPI
from .cfg__grpc__grpc_api_keys.sync_client import SyncCfgGrpcApiKeysAPI
from .cfg__grpc__grpc_configuration.sync_client import SyncCfgGrpcConfigurationAPI
from .cfg__grpc__grpc_monitoring.sync_client import SyncCfgGrpcMonitoringAPI
from .cfg__grpc__grpc_services.sync_client import SyncCfgGrpcServicesAPI
from .cfg__health.sync_client import SyncCfgHealthAPI
from .cfg__totp.sync_client import SyncCfgTotpAPI


class SyncAPIClient:
    """
    Synchronous API client for Django CFG API.

    Usage:
        >>> with SyncAPIClient(base_url='https://api.example.com') as client:
        ...     client.set_token('your-jwt-token')
        ...     users = client.users.list()
        ...     post = client.posts.create(data=new_post)
    """

    def __init__(
        self,
        base_url: str,
        logger_config: LoggerConfig | None = None,
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
        self._token: str | None = None

        # Initialize logger
        self.logger: APILogger | None = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.cfg_auth = SyncCfgAuthAPI(self._client)
        self.cfg_backup_codes = SyncCfgBackupCodesAPI(self._client)
        self.cfg_centrifugo_admin_api = SyncCfgCentrifugoAdminApiAPI(self._client)
        self.cfg_centrifugo_auth = SyncCfgCentrifugoAuthAPI(self._client)
        self.cfg_centrifugo_monitoring = SyncCfgCentrifugoMonitoringAPI(self._client)
        self.cfg_centrifugo_testing = SyncCfgCentrifugoTestingAPI(self._client)
        self.cfg_dashboard_api_zones = SyncCfgDashboardApiZonesAPI(self._client)
        self.cfg_dashboard_activity = SyncCfgDashboardActivityAPI(self._client)
        self.cfg_dashboard_charts = SyncCfgDashboardChartsAPI(self._client)
        self.cfg_dashboard_commands = SyncCfgDashboardCommandsAPI(self._client)
        self.cfg_dashboard_config = SyncCfgDashboardConfigAPI(self._client)
        self.cfg_dashboard_overview = SyncCfgDashboardOverviewAPI(self._client)
        self.cfg_dashboard_statistics = SyncCfgDashboardStatisticsAPI(self._client)
        self.cfg_dashboard_system = SyncCfgDashboardSystemAPI(self._client)
        self.cfg_dashboard_metrics = SyncCfgDashboardMetricsAPI(self._client)
        self.cfg_oauth = SyncCfgOauthAPI(self._client)
        self.cfg_rq_jobs = SyncCfgRqJobsAPI(self._client)
        self.cfg_rq_monitoring = SyncCfgRqMonitoringAPI(self._client)
        self.cfg_rq_queues = SyncCfgRqQueuesAPI(self._client)
        self.cfg_rq_registries = SyncCfgRqRegistriesAPI(self._client)
        self.cfg_rq_schedules = SyncCfgRqSchedulesAPI(self._client)
        self.cfg_rq_testing = SyncCfgRqTestingAPI(self._client)
        self.cfg_rq_workers = SyncCfgRqWorkersAPI(self._client)
        self.cfg_totp_management = SyncCfgTotpManagementAPI(self._client)
        self.cfg_totp_setup = SyncCfgTotpSetupAPI(self._client)
        self.cfg_totp_verification = SyncCfgTotpVerificationAPI(self._client)
        self.cfg_user_profile = SyncCfgUserProfileAPI(self._client)
        self.cfg_accounts = SyncCfgAccountsAPI(self._client)
        self.cfg_grpc_api_keys = SyncCfgGrpcApiKeysAPI(self._client)
        self.cfg_grpc_configuration = SyncCfgGrpcConfigurationAPI(self._client)
        self.cfg_grpc_monitoring = SyncCfgGrpcMonitoringAPI(self._client)
        self.cfg_grpc_services = SyncCfgGrpcServicesAPI(self._client)
        self.cfg_health = SyncCfgHealthAPI(self._client)
        self.cfg_totp = SyncCfgTotpAPI(self._client)

    def set_token(self, token: str) -> None:
        """
        Set JWT authentication token.

        Args:
            token: JWT access token
        """
        self._token = token
        self._client.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        """Clear authentication token."""
        self._token = None
        self._client.headers.pop("Authorization", None)

    def is_authenticated(self) -> bool:
        """Check if token is set."""
        return self._token is not None

    def __enter__(self) -> SyncAPIClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.close()

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()