from __future__ import annotations

import httpx

from .models import *


class SyncCfgSubscriptionsAPI:
    """Synchronous API endpoints for Subscriptions."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def subscribe_create(self, data: SubscribeRequest) -> SubscribeResponse:
        """
        Subscribe to Newsletter

        Subscribe an email address to a newsletter.
        """
        url = "/django_cfg_newsletter/subscribe/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return SubscribeResponse.model_validate(response.json())


    def list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedNewsletterSubscriptionList]:
        """
        List User Subscriptions

        Get a list of current user's active newsletter subscriptions.
        """
        url = "/django_cfg_newsletter/subscriptions/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedNewsletterSubscriptionList.model_validate(item) for item in data.get("results", [])]


    def unsubscribe_create(self, data: UnsubscribeRequest) -> SuccessResponse:
        """
        Unsubscribe from Newsletter

        Unsubscribe from a newsletter using subscription ID.
        """
        url = "/django_cfg_newsletter/unsubscribe/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return SuccessResponse.model_validate(response.json())


