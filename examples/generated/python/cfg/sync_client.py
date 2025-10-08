from __future__ import annotations

from typing import Any, Optional

import httpx

from .cfg__accounts__auth.sync_client import SyncCfgAuthAPI
from .cfg__newsletter__bulk_email.sync_client import SyncCfgBulkEmailAPI
from .cfg__newsletter__campaigns.sync_client import SyncCfgCampaignsAPI
from .cfg__leads__lead_submission.sync_client import SyncCfgLeadSubmissionAPI
from .cfg__newsletter__logs.sync_client import SyncCfgLogsAPI
from .cfg__newsletter__newsletters.sync_client import SyncCfgNewslettersAPI
from .cfg__newsletter__subscriptions.sync_client import SyncCfgSubscriptionsAPI
from .cfg__newsletter__testing.sync_client import SyncCfgTestingAPI
from .cfg__accounts__user_profile.sync_client import SyncCfgUserProfileAPI
from .cfg__payments__webhooks.sync_client import SyncCfgWebhooksAPI
from .cfg__accounts.sync_client import SyncCfgAccountsAPI
from .cfg__leads.sync_client import SyncCfgLeadsAPI
from .cfg__newsletter.sync_client import SyncCfgNewsletterAPI
from .cfg__support.sync_client import SyncCfgSupportAPI
from .cfg__payments.sync_client import SyncCfgPaymentsAPI
from .cfg__tasks.sync_client import SyncCfgTasksAPI
from .logger import APILogger, LoggerConfig
from .retry import RetryConfig, RetryAsyncClient


class SyncAPIClient:
    """
    Synchronous API client for Django CFG Sample API.

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
            timeout=30.0,
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
        self.cfg_lead_submission = SyncCfgLeadSubmissionAPI(self._client)
        self.cfg_logs = SyncCfgLogsAPI(self._client)
        self.cfg_newsletters = SyncCfgNewslettersAPI(self._client)
        self.cfg_subscriptions = SyncCfgSubscriptionsAPI(self._client)
        self.cfg_testing = SyncCfgTestingAPI(self._client)
        self.cfg_user_profile = SyncCfgUserProfileAPI(self._client)
        self.cfg_webhooks = SyncCfgWebhooksAPI(self._client)
        self.cfg_accounts = SyncCfgAccountsAPI(self._client)
        self.cfg_leads = SyncCfgLeadsAPI(self._client)
        self.cfg_newsletter = SyncCfgNewsletterAPI(self._client)
        self.cfg_support = SyncCfgSupportAPI(self._client)
        self.cfg_payments = SyncCfgPaymentsAPI(self._client)
        self.cfg_tasks = SyncCfgTasksAPI(self._client)

    def __enter__(self) -> 'SyncAPIClient':
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.close()

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()