from __future__ import annotations

import httpx

from .models import *


class SyncCfgPaymentsAPI:
    """Synchronous API endpoints for Cfg Payments."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def cfg_payments_admin_api_payments_list(self, currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None, status: str | None = None, user: int | None = None) -> list[PaginatedAdminPaymentListList]:
        """
        Admin ViewSet for payment management. Provides full CRUD operations for
        payments with admin-specific features.
        """
        url = "/cfg/payments/admin/api/payments/"
        response = self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedAdminPaymentListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_admin_api_payments_create(self, data: AdminPaymentCreateRequest) -> AdminPaymentCreate:
        """
        Create payment with enhanced error handling.
        """
        url = "/cfg/payments/admin/api/payments/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return AdminPaymentCreate.model_validate(response.json())


    def cfg_payments_admin_api_payments_retrieve(self, id: str) -> AdminPaymentDetail:
        """
        Admin ViewSet for payment management. Provides full CRUD operations for
        payments with admin-specific features.
        """
        url = f"/cfg/payments/admin/api/payments/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return AdminPaymentDetail.model_validate(response.json())


    def cfg_payments_admin_api_payments_update(self, id: str, data: AdminPaymentUpdateRequest) -> AdminPaymentUpdate:
        """
        Admin ViewSet for payment management. Provides full CRUD operations for
        payments with admin-specific features.
        """
        url = f"/cfg/payments/admin/api/payments/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return AdminPaymentUpdate.model_validate(response.json())


    def cfg_payments_admin_api_payments_partial_update(self, id: str, data: PatchedAdminPaymentUpdateRequest | None = None) -> AdminPaymentUpdate:
        """
        Admin ViewSet for payment management. Provides full CRUD operations for
        payments with admin-specific features.
        """
        url = f"/cfg/payments/admin/api/payments/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return AdminPaymentUpdate.model_validate(response.json())


    def cfg_payments_admin_api_payments_destroy(self, id: str) -> None:
        """
        Admin ViewSet for payment management. Provides full CRUD operations for
        payments with admin-specific features.
        """
        url = f"/cfg/payments/admin/api/payments/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_admin_api_payments_cancel_create(self, id: str) -> AdminPaymentDetail:
        """
        Cancel a payment.
        """
        url = f"/cfg/payments/admin/api/payments/{id}/cancel/"
        response = self._client.post(url)
        response.raise_for_status()
        return AdminPaymentDetail.model_validate(response.json())


    def cfg_payments_admin_api_payments_refresh_status_create(self, id: str) -> AdminPaymentDetail:
        """
        Refresh payment status from provider via AJAX.
        """
        url = f"/cfg/payments/admin/api/payments/{id}/refresh_status/"
        response = self._client.post(url)
        response.raise_for_status()
        return AdminPaymentDetail.model_validate(response.json())


    def cfg_payments_admin_api_payments_refund_create(self, id: str) -> AdminPaymentDetail:
        """
        Refund a payment.
        """
        url = f"/cfg/payments/admin/api/payments/{id}/refund/"
        response = self._client.post(url)
        response.raise_for_status()
        return AdminPaymentDetail.model_validate(response.json())


    def cfg_payments_admin_api_payments_stats_retrieve(self) -> AdminPaymentStats:
        """
        Get comprehensive payment statistics.
        """
        url = "/cfg/payments/admin/api/payments/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return AdminPaymentStats.model_validate(response.json())


    def cfg_payments_admin_api_stats_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedAdminPaymentStatsList]:
        """
        Get overview statistics.
        """
        url = "/cfg/payments/admin/api/stats/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedAdminPaymentStatsList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_admin_api_stats_retrieve(self, id: str) -> AdminPaymentStats:
        """
        Admin ViewSet for comprehensive system statistics. Provides aggregated
        statistics across all system components.
        """
        url = f"/cfg/payments/admin/api/stats/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return AdminPaymentStats.model_validate(response.json())


    def cfg_payments_admin_api_stats_payments_retrieve(self) -> AdminPaymentStats:
        """
        Get detailed payment statistics.
        """
        url = "/cfg/payments/admin/api/stats/payments/"
        response = self._client.get(url)
        response.raise_for_status()
        return AdminPaymentStats.model_validate(response.json())


    def cfg_payments_admin_api_stats_system_retrieve(self) -> AdminPaymentStats:
        """
        Get system health and performance statistics.
        """
        url = "/cfg/payments/admin/api/stats/system/"
        response = self._client.get(url)
        response.raise_for_status()
        return AdminPaymentStats.model_validate(response.json())


    def cfg_payments_admin_api_stats_webhooks_retrieve(self) -> AdminPaymentStats:
        """
        Get detailed webhook statistics.
        """
        url = "/cfg/payments/admin/api/stats/webhooks/"
        response = self._client.get(url)
        response.raise_for_status()
        return AdminPaymentStats.model_validate(response.json())


    def cfg_payments_admin_api_users_list(self, is_active: bool | None = None, is_staff: bool | None = None, is_superuser: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedAdminUserList]:
        """
        Override list to limit results for dropdown.
        """
        url = "/cfg/payments/admin/api/users/"
        response = self._client.get(url, params={"is_active": is_active if is_active is not None else None, "is_staff": is_staff if is_staff is not None else None, "is_superuser": is_superuser if is_superuser is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedAdminUserList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_admin_api_users_retrieve(self, id: int) -> AdminUser:
        """
        Admin ViewSet for user management. Provides read-only access to users
        for admin interface.
        """
        url = f"/cfg/payments/admin/api/users/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return AdminUser.model_validate(response.json())


    def cfg_payments_admin_api_webhook_test_test_create(self, data: WebhookStatsRequest) -> WebhookStats:
        """
        Test webhook endpoint. Sends a test webhook to the specified URL with
        the given event type. Useful for developers to test their webhook
        implementations.
        """
        url = "/cfg/payments/admin/api/webhook-test/test/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return WebhookStats.model_validate(response.json())


    def cfg_payments_admin_api_webhooks_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedWebhookStatsList]:
        """
        List webhook providers and configurations with real ngrok URLs.
        """
        url = "/cfg/payments/admin/api/webhooks/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedWebhookStatsList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_admin_api_webhooks_retrieve(self, id: str) -> WebhookStats:
        """
        Admin ViewSet for webhook configuration management. Read-only view for
        webhook configurations and provider info. Requires admin permissions.
        """
        url = f"/cfg/payments/admin/api/webhooks/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return WebhookStats.model_validate(response.json())


    def cfg_payments_admin_api_webhooks_events_list(self, webhook_pk: str, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedWebhookEventListList]:
        """
        List webhook events with filtering and pagination.
        """
        url = f"/cfg/payments/admin/api/webhooks/{webhook_pk}/events/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedWebhookEventListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_admin_api_webhooks_events_retrieve(self, id: str, webhook_pk: str) -> list[WebhookEventList]:
        """
        Admin ViewSet for webhook events management. Provides listing,
        filtering, and actions for webhook events. Requires admin permissions.
        """
        url = f"/cfg/payments/admin/api/webhooks/{webhook_pk}/events/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        data = response.json()
        return [WebhookEventList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_admin_api_webhooks_events_retry_create(self, id: str, webhook_pk: str, data: WebhookEventListRequest) -> WebhookEventList:
        """
        Retry a failed webhook event.
        """
        url = f"/cfg/payments/admin/api/webhooks/{webhook_pk}/events/{id}/retry/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return WebhookEventList.model_validate(response.json())


    def cfg_payments_admin_api_webhooks_events_clear_all_create(self, webhook_pk: str, data: WebhookEventListRequest) -> WebhookEventList:
        """
        Clear all webhook events.
        """
        url = f"/cfg/payments/admin/api/webhooks/{webhook_pk}/events/clear_all/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return WebhookEventList.model_validate(response.json())


    def cfg_payments_admin_api_webhooks_events_retry_failed_create(self, webhook_pk: str, data: WebhookEventListRequest) -> WebhookEventList:
        """
        Retry all failed webhook events.
        """
        url = f"/cfg/payments/admin/api/webhooks/{webhook_pk}/events/retry_failed/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return WebhookEventList.model_validate(response.json())


    def cfg_payments_admin_api_webhooks_stats_retrieve(self) -> WebhookStats:
        """
        Get webhook statistics.
        """
        url = "/cfg/payments/admin/api/webhooks/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return WebhookStats.model_validate(response.json())


    def cfg_payments_api_keys_list(self, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, user: int | None = None) -> list[PaginatedAPIKeyListList]:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = "/cfg/payments/api-keys/"
        response = self._client.get(url, params={"is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedAPIKeyListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_api_keys_create(self, data: APIKeyCreateRequest) -> APIKeyCreate:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = "/cfg/payments/api-keys/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIKeyCreate.model_validate(response.json())


    def cfg_payments_api_keys_retrieve(self, id: str) -> APIKeyDetail:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/cfg/payments/api-keys/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_api_keys_update(self, id: str, data: APIKeyUpdateRequest) -> APIKeyUpdate:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/cfg/payments/api-keys/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    def cfg_payments_api_keys_partial_update(self, id: str, data: PatchedAPIKeyUpdateRequest | None = None) -> APIKeyUpdate:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/cfg/payments/api-keys/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    def cfg_payments_api_keys_destroy(self, id: str) -> None:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/cfg/payments/api-keys/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_api_keys_perform_action_create(self, id: str) -> APIKeyDetail:
        """
        Perform action on API key. POST /api/api-keys/{id}/perform_action/
        """
        url = f"/cfg/payments/api-keys/{id}/perform_action/"
        response = self._client.post(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_api_keys_analytics_retrieve(self) -> APIKeyDetail:
        """
        Get API key analytics. GET /api/api-keys/analytics/?days=30
        """
        url = "/cfg/payments/api-keys/analytics/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_api_keys_by_user_retrieve(self) -> APIKeyDetail:
        """
        Get API keys grouped by user. GET /api/api-keys/by_user/
        """
        url = "/cfg/payments/api-keys/by_user/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_api_keys_create_create(self, data: APIKeyCreateRequest) -> APIKeyCreate:
        """
        Standalone API key creation endpoint: /api/api-keys/create/ Simplified
        endpoint for API key creation.
        """
        url = "/cfg/payments/api-keys/create/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIKeyCreate.model_validate(response.json())


    def cfg_payments_api_keys_expiring_soon_retrieve(self) -> APIKeyDetail:
        """
        Get API keys expiring soon. GET /api/api-keys/expiring_soon/?days=7
        """
        url = "/cfg/payments/api-keys/expiring_soon/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_api_keys_health_retrieve(self) -> APIKeyDetail:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/api-keys/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_api_keys_stats_retrieve(self) -> APIKeyDetail:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/api-keys/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_api_keys_validate_create(self, data: APIKeyValidationRequest) -> APIKeyValidationResponse:
        """
        Validate API Key (Standalone)

        Standalone endpoint to validate an API key and return key information
        """
        url = "/cfg/payments/api-keys/validate/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIKeyValidationResponse.model_validate(response.json())


    def cfg_payments_api_keys_validate_key_create(self, data: APIKeyValidationRequest) -> APIKeyValidationResponse:
        """
        Validate API Key

        Validate an API key and return key information
        """
        url = "/cfg/payments/api-keys/validate_key/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIKeyValidationResponse.model_validate(response.json())


    def cfg_payments_balances_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, user: int | None = None) -> list[PaginatedUserBalanceList]:
        """
        User balance ViewSet: /api/balances/ Read-only access to user balances
        with statistics.
        """
        url = "/cfg/payments/balances/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedUserBalanceList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_balances_retrieve(self, id: int) -> UserBalance:
        """
        User balance ViewSet: /api/balances/ Read-only access to user balances
        with statistics.
        """
        url = f"/cfg/payments/balances/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    def cfg_payments_balances_analytics_retrieve(self) -> UserBalance:
        """
        Get balance analytics. GET /api/balances/analytics/?days=30
        """
        url = "/cfg/payments/balances/analytics/"
        response = self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    def cfg_payments_balances_health_retrieve(self) -> UserBalance:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/balances/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    def cfg_payments_balances_stats_retrieve(self) -> UserBalance:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/balances/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    def cfg_payments_balances_summary_retrieve(self) -> UserBalance:
        """
        Get balance summary for all users. GET /api/balances/summary/
        """
        url = "/cfg/payments/balances/summary/"
        response = self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    def cfg_payments_currencies_list(self, currency_type: str | None = None, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedCurrencyListList]:
        """
        Currency ViewSet: /api/currencies/ Read-only access to currency
        information with conversion capabilities.
        """
        url = "/cfg/payments/currencies/"
        response = self._client.get(url, params={"currency_type": currency_type if currency_type is not None else None, "is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedCurrencyListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_currencies_create(self) -> Currency:
        """
        Disable create action.
        """
        url = "/cfg/payments/currencies/"
        response = self._client.post(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_retrieve(self, id: int) -> Currency:
        """
        Currency ViewSet: /api/currencies/ Read-only access to currency
        information with conversion capabilities.
        """
        url = f"/cfg/payments/currencies/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_networks_retrieve(self, id: int) -> Currency:
        """
        Get networks for specific currency. GET /api/currencies/{id}/networks/
        """
        url = f"/cfg/payments/currencies/{id}/networks/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_providers_retrieve(self, id: int) -> Currency:
        """
        Get providers supporting specific currency. GET
        /api/currencies/{id}/providers/
        """
        url = f"/cfg/payments/currencies/{id}/providers/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_convert_create(self) -> Currency:
        """
        Convert between currencies. POST /api/currencies/convert/
        """
        url = "/cfg/payments/currencies/convert/"
        response = self._client.post(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_crypto_retrieve(self) -> Currency:
        """
        Get only cryptocurrencies. GET /api/currencies/crypto/
        """
        url = "/cfg/payments/currencies/crypto/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_fiat_retrieve(self) -> Currency:
        """
        Get only fiat currencies. GET /api/currencies/fiat/
        """
        url = "/cfg/payments/currencies/fiat/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_health_retrieve(self) -> Currency:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/currencies/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_rates_retrieve(self, base_currency: str, currencies: str) -> Currency:
        """
        Get exchange rates

        Get current exchange rates for specified currencies
        """
        url = "/cfg/payments/currencies/rates/"
        response = self._client.get(url, params={"base_currency": base_currency, "currencies": currencies})
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_stable_retrieve(self) -> Currency:
        """
        Get only stablecoins. GET /api/currencies/stable/
        """
        url = "/cfg/payments/currencies/stable/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_stats_retrieve(self) -> Currency:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/currencies/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_currencies_supported_retrieve(self, currency_type: str | None = None, provider: str | None = None) -> Currency:
        """
        Get supported currencies

        Get list of supported currencies from payment providers
        """
        url = "/cfg/payments/currencies/supported/"
        response = self._client.get(url, params={"currency_type": currency_type if currency_type is not None else None, "provider": provider if provider is not None else None})
        response.raise_for_status()
        return Currency.model_validate(response.json())


    def cfg_payments_endpoint_groups_list(self, is_enabled: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedEndpointGroupList]:
        """
        Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
        endpoint group information.
        """
        url = "/cfg/payments/endpoint-groups/"
        response = self._client.get(url, params={"is_enabled": is_enabled if is_enabled is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedEndpointGroupList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_endpoint_groups_retrieve(self, id: int) -> EndpointGroup:
        """
        Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
        endpoint group information.
        """
        url = f"/cfg/payments/endpoint-groups/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    def cfg_payments_endpoint_groups_available_retrieve(self) -> EndpointGroup:
        """
        Get available endpoint groups for subscription. GET
        /api/endpoint-groups/available/
        """
        url = "/cfg/payments/endpoint-groups/available/"
        response = self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    def cfg_payments_endpoint_groups_health_retrieve(self) -> EndpointGroup:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/endpoint-groups/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    def cfg_payments_endpoint_groups_stats_retrieve(self) -> EndpointGroup:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/endpoint-groups/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    def cfg_payments_health_retrieve(self) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_networks_list(self, is_active: bool | None = None, native_currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedNetworkList]:
        """
        Network ViewSet: /api/networks/ Read-only access to blockchain network
        information.
        """
        url = "/cfg/payments/networks/"
        response = self._client.get(url, params={"is_active": is_active if is_active is not None else None, "native_currency__code": native_currency__code if native_currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedNetworkList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_networks_retrieve(self, id: int) -> Network:
        """
        Network ViewSet: /api/networks/ Read-only access to blockchain network
        information.
        """
        url = f"/cfg/payments/networks/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    def cfg_payments_networks_by_currency_retrieve(self) -> Network:
        """
        Get networks grouped by currency. GET /api/networks/by_currency/
        """
        url = "/cfg/payments/networks/by_currency/"
        response = self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    def cfg_payments_networks_health_retrieve(self) -> Network:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/networks/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    def cfg_payments_networks_stats_retrieve(self) -> Network:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/networks/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    def cfg_payments_overview_dashboard_api_keys_overview_retrieve(self) -> APIKeysOverview:
        """
        API Keys Overview

        Get API keys overview
        """
        url = "/cfg/payments/overview/dashboard/api_keys_overview/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeysOverview.model_validate(response.json())


    def cfg_payments_overview_dashboard_balance_overview_retrieve(self) -> BalanceOverview:
        """
        Balance Overview

        Get user balance overview
        """
        url = "/cfg/payments/overview/dashboard/balance_overview/"
        response = self._client.get(url)
        response.raise_for_status()
        return BalanceOverview.model_validate(response.json())


    def cfg_payments_overview_dashboard_chart_data_retrieve(self, period: str | None = None) -> PaymentsChartResponse:
        """
        Payments Chart Data

        Get chart data for payments visualization
        """
        url = "/cfg/payments/overview/dashboard/chart_data/"
        response = self._client.get(url, params={"period": period if period is not None else None})
        response.raise_for_status()
        return PaymentsChartResponse.model_validate(response.json())


    def cfg_payments_overview_dashboard_metrics_retrieve(self) -> PaymentsMetrics:
        """
        Payments Dashboard Metrics

        Get payments dashboard metrics including balance, subscriptions, API
        keys, and payments
        """
        url = "/cfg/payments/overview/dashboard/metrics/"
        response = self._client.get(url)
        response.raise_for_status()
        return PaymentsMetrics.model_validate(response.json())


    def cfg_payments_overview_dashboard_overview_retrieve(self) -> PaymentsDashboardOverview:
        """
        Payments Dashboard Overview

        Get complete payments dashboard overview with metrics, recent payments,
        and analytics
        """
        url = "/cfg/payments/overview/dashboard/overview/"
        response = self._client.get(url)
        response.raise_for_status()
        return PaymentsDashboardOverview.model_validate(response.json())


    def cfg_payments_overview_dashboard_payment_analytics_retrieve(self, limit: int | None = None) -> PaymentAnalyticsResponse:
        """
        Payment Analytics

        Get analytics for payments by currency and provider
        """
        url = "/cfg/payments/overview/dashboard/payment_analytics/"
        response = self._client.get(url, params={"limit": limit if limit is not None else None})
        response.raise_for_status()
        return PaymentAnalyticsResponse.model_validate(response.json())


    def cfg_payments_overview_dashboard_recent_payments_list(self, limit: int | None = None, page: int | None = None, page_size: int | None = None) -> list[PaginatedRecentPaymentList]:
        """
        Recent Payments

        Get recent payments for the user
        """
        url = "/cfg/payments/overview/dashboard/recent_payments/"
        response = self._client.get(url, params={"limit": limit if limit is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedRecentPaymentList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_overview_dashboard_recent_transactions_list(self, limit: int | None = None, page: int | None = None, page_size: int | None = None) -> list[PaginatedRecentTransactionList]:
        """
        Recent Transactions

        Get recent balance transactions for the user
        """
        url = "/cfg/payments/overview/dashboard/recent_transactions/"
        response = self._client.get(url, params={"limit": limit if limit is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedRecentTransactionList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_overview_dashboard_subscription_overview_retrieve(self) -> SubscriptionOverview:
        """
        Subscription Overview

        Get current subscription overview
        """
        url = "/cfg/payments/overview/dashboard/subscription_overview/"
        response = self._client.get(url)
        response.raise_for_status()
        return SubscriptionOverview.model_validate(response.json())


    def cfg_payments_payments_list(self, currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None, status: str | None = None, user: int | None = None) -> list[PaginatedPaymentListList]:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = "/cfg/payments/payments/"
        response = self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPaymentListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_payments_create(self, data: PaymentCreateRequest) -> PaymentCreate:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = "/cfg/payments/payments/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    def cfg_payments_payments_retrieve(self, id: str) -> Payment:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/cfg/payments/payments/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_update(self, id: str, data: PaymentRequest) -> Payment:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/cfg/payments/payments/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_partial_update(self, id: str, data: PatchedPaymentRequest | None = None) -> Payment:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/cfg/payments/payments/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_destroy(self, id: str) -> None:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/cfg/payments/payments/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_payments_cancel_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Cancel payment. POST /api/v1/payments/{id}/cancel/
        """
        url = f"/cfg/payments/payments/{id}/cancel/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_check_status_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Check payment status with provider. POST
        /api/v1/payments/{id}/check_status/
        """
        url = f"/cfg/payments/payments/{id}/check_status/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_analytics_retrieve(self) -> Payment:
        """
        Get payment analytics. GET /api/v1/payments/analytics/?days=30
        """
        url = "/cfg/payments/payments/analytics/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_by_provider_retrieve(self) -> Payment:
        """
        Get payments grouped by provider. GET /api/v1/payments/by_provider/
        """
        url = "/cfg/payments/payments/by_provider/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_create_create(self, data: PaymentCreateRequest) -> PaymentCreate:
        """
        Standalone payment creation endpoint: /api/v1/payments/create/
        Simplified endpoint for payment creation without full ViewSet overhead.
        """
        url = "/cfg/payments/payments/create/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    def cfg_payments_payments_health_retrieve(self) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/payments/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_stats_retrieve(self) -> Payment:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/payments/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_payments_status_retrieve(self, id: str) -> Payment:
        """
        Standalone payment status endpoint: /api/v1/payments/{id}/status/ Quick
        status check without full ViewSet overhead.
        """
        url = f"/cfg/payments/payments/status/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_provider_currencies_list(self, currency__code: str | None = None, is_enabled: bool | None = None, network__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None) -> list[PaginatedProviderCurrencyList]:
        """
        Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
        provider-specific currency information.
        """
        url = "/cfg/payments/provider-currencies/"
        response = self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "is_enabled": is_enabled if is_enabled is not None else None, "network__code": network__code if network__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedProviderCurrencyList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_provider_currencies_retrieve(self, id: int) -> ProviderCurrency:
        """
        Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
        provider-specific currency information.
        """
        url = f"/cfg/payments/provider-currencies/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    def cfg_payments_provider_currencies_by_provider_retrieve(self) -> ProviderCurrency:
        """
        Get provider currencies grouped by provider. GET
        /api/provider-currencies/by_provider/
        """
        url = "/cfg/payments/provider-currencies/by_provider/"
        response = self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    def cfg_payments_provider_currencies_health_retrieve(self) -> ProviderCurrency:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/provider-currencies/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    def cfg_payments_provider_currencies_limits_retrieve(self) -> ProviderCurrency:
        """
        Get currency limits by provider. GET
        /api/provider-currencies/limits/?provider=nowpayments
        """
        url = "/cfg/payments/provider-currencies/limits/"
        response = self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    def cfg_payments_provider_currencies_stats_retrieve(self) -> ProviderCurrency:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/provider-currencies/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    def cfg_payments_subscriptions_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None, tier: str | None = None, user: int | None = None) -> list[PaginatedSubscriptionListList]:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = "/cfg/payments/subscriptions/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "tier": tier if tier is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedSubscriptionListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_subscriptions_create(self, data: SubscriptionCreateRequest) -> SubscriptionCreate:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = "/cfg/payments/subscriptions/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return SubscriptionCreate.model_validate(response.json())


    def cfg_payments_subscriptions_retrieve(self, id: str) -> Subscription:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/cfg/payments/subscriptions/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_update(self, id: str, data: SubscriptionRequest) -> Subscription:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/cfg/payments/subscriptions/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_partial_update(self, id: str, data: PatchedSubscriptionRequest | None = None) -> Subscription:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/cfg/payments/subscriptions/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_destroy(self, id: str) -> None:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/cfg/payments/subscriptions/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_subscriptions_increment_usage_create(self, id: str, data: SubscriptionRequest) -> Subscription:
        """
        Increment subscription usage. POST
        /api/subscriptions/{id}/increment_usage/
        """
        url = f"/cfg/payments/subscriptions/{id}/increment_usage/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_update_status_create(self, id: str, data: SubscriptionRequest) -> Subscription:
        """
        Update subscription status. POST /api/subscriptions/{id}/update_status/
        """
        url = f"/cfg/payments/subscriptions/{id}/update_status/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_analytics_retrieve(self) -> Subscription:
        """
        Get subscription analytics. GET /api/subscriptions/analytics/?days=30
        """
        url = "/cfg/payments/subscriptions/analytics/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_by_status_retrieve(self) -> Subscription:
        """
        Get subscriptions grouped by status. GET /api/subscriptions/by_status/
        """
        url = "/cfg/payments/subscriptions/by_status/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_by_tier_retrieve(self) -> Subscription:
        """
        Get subscriptions grouped by tier. GET /api/subscriptions/by_tier/
        """
        url = "/cfg/payments/subscriptions/by_tier/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_health_retrieve(self) -> Subscription:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/subscriptions/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_subscriptions_stats_retrieve(self) -> Subscription:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/subscriptions/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_tariffs_list(self, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedTariffList]:
        """
        Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
        subscription selection.
        """
        url = "/cfg/payments/tariffs/"
        response = self._client.get(url, params={"is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedTariffList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_tariffs_retrieve(self, id: int) -> Tariff:
        """
        Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
        subscription selection.
        """
        url = f"/cfg/payments/tariffs/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    def cfg_payments_tariffs_endpoint_groups_retrieve(self, id: int) -> Tariff:
        """
        Get endpoint groups for specific tariff. GET
        /api/tariffs/{id}/endpoint_groups/
        """
        url = f"/cfg/payments/tariffs/{id}/endpoint_groups/"
        response = self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    def cfg_payments_tariffs_free_retrieve(self) -> Tariff:
        """
        Get free tariffs. GET /api/tariffs/free/
        """
        url = "/cfg/payments/tariffs/free/"
        response = self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    def cfg_payments_tariffs_health_retrieve(self) -> Tariff:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/tariffs/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    def cfg_payments_tariffs_paid_retrieve(self) -> Tariff:
        """
        Get paid tariffs. GET /api/tariffs/paid/
        """
        url = "/cfg/payments/tariffs/paid/"
        response = self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    def cfg_payments_tariffs_stats_retrieve(self) -> Tariff:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/tariffs/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    def cfg_payments_transactions_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, payment_id: str | None = None, search: str | None = None, transaction_type: str | None = None, user: int | None = None) -> list[PaginatedTransactionList]:
        """
        Transaction ViewSet: /api/transactions/ Read-only access to transaction
        history with filtering.
        """
        url = "/cfg/payments/transactions/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "payment_id": payment_id if payment_id is not None else None, "search": search if search is not None else None, "transaction_type": transaction_type if transaction_type is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedTransactionList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_transactions_retrieve(self, id: str) -> Transaction:
        """
        Transaction ViewSet: /api/transactions/ Read-only access to transaction
        history with filtering.
        """
        url = f"/cfg/payments/transactions/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    def cfg_payments_transactions_by_type_retrieve(self) -> Transaction:
        """
        Get transactions grouped by type. GET /api/transactions/by_type/
        """
        url = "/cfg/payments/transactions/by_type/"
        response = self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    def cfg_payments_transactions_health_retrieve(self) -> Transaction:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/transactions/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    def cfg_payments_transactions_recent_retrieve(self) -> Transaction:
        """
        Get recent transactions. GET /api/transactions/recent/?limit=10
        """
        url = "/cfg/payments/transactions/recent/"
        response = self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    def cfg_payments_transactions_stats_retrieve(self) -> Transaction:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/transactions/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    def cfg_payments_users_list(self, currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None, status: str | None = None) -> list[PaginatedPaymentListList]:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = "/cfg/payments/users/"
        response = self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPaymentListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_users_create(self, data: PaymentCreateRequest) -> PaymentCreate:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = "/cfg/payments/users/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    def cfg_payments_users_retrieve(self, id: str) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_update(self, id: str, data: PaymentRequest) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_partial_update(self, id: str, data: PatchedPaymentRequest | None = None) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_destroy(self, id: str) -> None:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_users_cancel_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
        """
        url = f"/cfg/payments/users/{id}/cancel/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_check_status_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Check payment status with provider. POST
        /api/v1/users/{user_id}/payments/{id}/check_status/
        """
        url = f"/cfg/payments/users/{id}/check_status/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_api_keys_list(self, user_pk: int, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedAPIKeyListList]:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/"
        response = self._client.get(url, params={"is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedAPIKeyListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_users_api_keys_create(self, user_pk: int, data: APIKeyCreateRequest) -> APIKeyCreate:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIKeyCreate.model_validate(response.json())


    def cfg_payments_users_api_keys_retrieve(self, id: str, user_pk: int) -> APIKeyDetail:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_users_api_keys_update(self, id: str, user_pk: int, data: APIKeyUpdateRequest) -> APIKeyUpdate:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    def cfg_payments_users_api_keys_partial_update(self, id: str, user_pk: int, data: PatchedAPIKeyUpdateRequest | None = None) -> APIKeyUpdate:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    def cfg_payments_users_api_keys_destroy(self, id: str, user_pk: int) -> None:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_users_api_keys_perform_action_create(self, id: str, user_pk: int) -> APIKeyDetail:
        """
        Perform action on API key. POST
        /api/users/{user_id}/api-keys/{id}/perform_action/
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/{id}/perform_action/"
        response = self._client.post(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_users_api_keys_active_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Get user's active API keys. GET /api/users/{user_id}/api-keys/active/
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/active/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_users_api_keys_health_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_users_api_keys_stats_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_users_api_keys_summary_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Get user API key summary. GET /api/users/{user_id}/api-keys/summary/
        """
        url = f"/cfg/payments/users/{user_pk}/api-keys/summary/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    def cfg_payments_users_payments_list(self, user_pk: int, currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None, status: str | None = None) -> list[PaginatedPaymentListList]:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/"
        response = self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPaymentListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_users_payments_create(self, user_pk: int, data: PaymentCreateRequest) -> PaymentCreate:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    def cfg_payments_users_payments_retrieve(self, id: str, user_pk: int) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_payments_update(self, id: str, user_pk: int, data: PaymentRequest) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_payments_partial_update(self, id: str, user_pk: int, data: PatchedPaymentRequest | None = None) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_payments_destroy(self, id: str, user_pk: int) -> None:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_users_payments_cancel_create(self, id: str, user_pk: int, data: PaymentRequest) -> Payment:
        """
        Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
        """
        url = f"/cfg/payments/users/{user_pk}/payments/{id}/cancel/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_payments_check_status_create(self, id: str, user_pk: int, data: PaymentRequest) -> Payment:
        """
        Check payment status with provider. POST
        /api/v1/users/{user_id}/payments/{id}/check_status/
        """
        url = f"/cfg/payments/users/{user_pk}/payments/{id}/check_status/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_payments_health_retrieve(self, user_pk: int) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_payments_stats_retrieve(self, user_pk: int) -> Payment:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = f"/cfg/payments/users/{user_pk}/payments/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_payments_summary_retrieve(self, user_pk: int) -> Payment:
        """
        Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
        """
        url = f"/cfg/payments/users/{user_pk}/payments/summary/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_subscriptions_list(self, user_pk: int, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None, tier: str | None = None) -> list[PaginatedSubscriptionListList]:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "tier": tier if tier is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedSubscriptionListList.model_validate(item) for item in data.get("results", [])]


    def cfg_payments_users_subscriptions_create(self, user_pk: int, data: SubscriptionCreateRequest) -> SubscriptionCreate:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return SubscriptionCreate.model_validate(response.json())


    def cfg_payments_users_subscriptions_retrieve(self, id: str, user_pk: int) -> Subscription:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_update(self, id: str, user_pk: int, data: SubscriptionRequest) -> Subscription:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_partial_update(self, id: str, user_pk: int, data: PatchedSubscriptionRequest | None = None) -> Subscription:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_destroy(self, id: str, user_pk: int) -> None:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_payments_users_subscriptions_increment_usage_create(self, id: str, user_pk: int, data: SubscriptionRequest) -> Subscription:
        """
        Increment subscription usage. POST
        /api/users/{user_id}/subscriptions/{id}/increment_usage/
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/{id}/increment_usage/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_update_status_create(self, id: str, user_pk: int, data: SubscriptionRequest) -> Subscription:
        """
        Update subscription status. POST
        /api/users/{user_id}/subscriptions/{id}/update_status/
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/{id}/update_status/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_active_retrieve(self, user_pk: int) -> Subscription:
        """
        Get user's active subscription. GET
        /api/users/{user_id}/subscriptions/active/
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/active/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_health_retrieve(self, user_pk: int) -> Subscription:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_stats_retrieve(self, user_pk: int) -> Subscription:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_subscriptions_summary_retrieve(self, user_pk: int) -> Subscription:
        """
        Get user subscription summary. GET
        /api/users/{user_id}/subscriptions/summary/
        """
        url = f"/cfg/payments/users/{user_pk}/subscriptions/summary/"
        response = self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    def cfg_payments_users_health_retrieve(self) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/cfg/payments/users/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_stats_retrieve(self) -> Payment:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/cfg/payments/users/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    def cfg_payments_users_summary_retrieve(self) -> Payment:
        """
        Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
        """
        url = "/cfg/payments/users/summary/"
        response = self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


