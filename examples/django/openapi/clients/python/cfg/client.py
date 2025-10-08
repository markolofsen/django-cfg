from __future__ import annotations

from typing import Any, Optional

import httpx

from .cfg__accounts__auth import CfgAuthAPI
from .cfg__newsletter__bulk_email import CfgBulkEmailAPI
from .cfg__newsletter__campaigns import CfgCampaignsAPI
from .cfg__leads__lead_submission import CfgLeadSubmissionAPI
from .cfg__newsletter__logs import CfgLogsAPI
from .cfg__newsletter__newsletters import CfgNewslettersAPI
from .cfg__newsletter__subscriptions import CfgSubscriptionsAPI
from .cfg__newsletter__testing import CfgTestingAPI
from .cfg__accounts__user_profile import CfgUserProfileAPI
from .cfg__payments__webhooks import CfgWebhooksAPI
from .cfg__accounts import CfgAccountsAPI
from .cfg__leads import CfgLeadsAPI
from .cfg__newsletter import CfgNewsletterAPI
from .cfg__support import CfgSupportAPI
from .cfg__payments import CfgPaymentsAPI
from .cfg__tasks import CfgTasksAPI
from .logger import APILogger, LoggerConfig


class APIClient:
    """
    Async API client for Django CFG Sample API.

    Usage:
        >>> async with APIClient(base_url='https://api.example.com') as client:
        ...     users = await client.users.list()
        ...     post = await client.posts.create(data=new_post)
    """

    def __init__(
        self,
        base_url: str,
        logger_config: Optional[LoggerConfig] = None,
        **kwargs: Any,
    ):
        """
        Initialize API client.

        Args:
            base_url: Base API URL (e.g., 'https://api.example.com')
            logger_config: Logger configuration (None to disable logging)
            **kwargs: Additional httpx.AsyncClient kwargs
        """
        self.base_url = base_url.rstrip('/')
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
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
        self.cfg_lead_submission = CfgLeadSubmissionAPI(self._client)
        self.cfg_logs = CfgLogsAPI(self._client)
        self.cfg_newsletters = CfgNewslettersAPI(self._client)
        self.cfg_subscriptions = CfgSubscriptionsAPI(self._client)
        self.cfg_testing = CfgTestingAPI(self._client)
        self.cfg_user_profile = CfgUserProfileAPI(self._client)
        self.cfg_webhooks = CfgWebhooksAPI(self._client)
        self.cfg_accounts = CfgAccountsAPI(self._client)
        self.cfg_leads = CfgLeadsAPI(self._client)
        self.cfg_newsletter = CfgNewsletterAPI(self._client)
        self.cfg_support = CfgSupportAPI(self._client)
        self.cfg_payments = CfgPaymentsAPI(self._client)
        self.cfg_tasks = CfgTasksAPI(self._client)

    async def __aenter__(self) -> 'APIClient':
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.aclose()

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()