from __future__ import annotations

import httpx

from .models import *


class CfgPaymentsAPI:
    """API endpoints for Payments."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def api_keys_list(self, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, user: int | None = None) -> list[PaginatedAPIKeyListList]:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = "/payments/api-keys/"
        response = await self._client.get(url, params={"is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedAPIKeyListList.model_validate(item) for item in data.get("results", [])]


    async def api_keys_create(self, data: APIKeyCreateRequest) -> APIKeyCreate:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = "/payments/api-keys/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIKeyCreate.model_validate(response.json())


    async def api_keys_retrieve(self, id: str) -> APIKeyDetail:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/payments/api-keys/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def api_keys_update(self, id: str, data: APIKeyUpdateRequest) -> APIKeyUpdate:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/payments/api-keys/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    async def api_keys_partial_update(self, id: str, data: PatchedAPIKeyUpdateRequest | None = None) -> APIKeyUpdate:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/payments/api-keys/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    async def api_keys_destroy(self, id: str) -> None:
        """
        Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
        all API keys with filtering and stats.
        """
        url = f"/payments/api-keys/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def api_keys_perform_action_create(self, id: str) -> APIKeyDetail:
        """
        Perform action on API key. POST /api/api-keys/{id}/perform_action/
        """
        url = f"/payments/api-keys/{id}/perform_action/"
        response = await self._client.post(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def api_keys_analytics_retrieve(self) -> APIKeyDetail:
        """
        Get API key analytics. GET /api/api-keys/analytics/?days=30
        """
        url = "/payments/api-keys/analytics/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def api_keys_by_user_retrieve(self) -> APIKeyDetail:
        """
        Get API keys grouped by user. GET /api/api-keys/by_user/
        """
        url = "/payments/api-keys/by_user/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def api_keys_create_create(self, data: APIKeyCreateRequest) -> APIKeyCreate:
        """
        Standalone API key creation endpoint: /api/api-keys/create/ Simplified
        endpoint for API key creation.
        """
        url = "/payments/api-keys/create/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIKeyCreate.model_validate(response.json())


    async def api_keys_expiring_soon_retrieve(self) -> APIKeyDetail:
        """
        Get API keys expiring soon. GET /api/api-keys/expiring_soon/?days=7
        """
        url = "/payments/api-keys/expiring_soon/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def api_keys_health_retrieve(self) -> APIKeyDetail:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/api-keys/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def api_keys_stats_retrieve(self) -> APIKeyDetail:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/api-keys/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def api_keys_validate_create(self, data: APIKeyValidationRequest) -> APIKeyValidationResponse:
        """
        Validate API Key (Standalone)

        Standalone endpoint to validate an API key and return key information
        """
        url = "/payments/api-keys/validate/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIKeyValidationResponse.model_validate(response.json())


    async def api_keys_validate_key_create(self, data: APIKeyValidationRequest) -> APIKeyValidationResponse:
        """
        Validate API Key

        Validate an API key and return key information
        """
        url = "/payments/api-keys/validate_key/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIKeyValidationResponse.model_validate(response.json())


    async def balances_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, user: int | None = None) -> list[PaginatedUserBalanceList]:
        """
        User balance ViewSet: /api/balances/ Read-only access to user balances
        with statistics.
        """
        url = "/payments/balances/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedUserBalanceList.model_validate(item) for item in data.get("results", [])]


    async def balances_retrieve(self, id: int) -> UserBalance:
        """
        User balance ViewSet: /api/balances/ Read-only access to user balances
        with statistics.
        """
        url = f"/payments/balances/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    async def balances_analytics_retrieve(self) -> UserBalance:
        """
        Get balance analytics. GET /api/balances/analytics/?days=30
        """
        url = "/payments/balances/analytics/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    async def balances_health_retrieve(self) -> UserBalance:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/balances/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    async def balances_stats_retrieve(self) -> UserBalance:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/balances/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    async def balances_summary_retrieve(self) -> UserBalance:
        """
        Get balance summary for all users. GET /api/balances/summary/
        """
        url = "/payments/balances/summary/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserBalance.model_validate(response.json())


    async def currencies_list(self, currency_type: str | None = None, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedCurrencyListList]:
        """
        Currency ViewSet: /api/currencies/ Read-only access to currency
        information with conversion capabilities.
        """
        url = "/payments/currencies/"
        response = await self._client.get(url, params={"currency_type": currency_type if currency_type is not None else None, "is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedCurrencyListList.model_validate(item) for item in data.get("results", [])]


    async def currencies_create(self) -> Currency:
        """
        Disable create action.
        """
        url = "/payments/currencies/"
        response = await self._client.post(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_retrieve(self, id: int) -> Currency:
        """
        Currency ViewSet: /api/currencies/ Read-only access to currency
        information with conversion capabilities.
        """
        url = f"/payments/currencies/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_networks_retrieve(self, id: int) -> Currency:
        """
        Get networks for specific currency. GET /api/currencies/{id}/networks/
        """
        url = f"/payments/currencies/{id}/networks/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_providers_retrieve(self, id: int) -> Currency:
        """
        Get providers supporting specific currency. GET
        /api/currencies/{id}/providers/
        """
        url = f"/payments/currencies/{id}/providers/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_convert_create(self) -> Currency:
        """
        Convert between currencies. POST /api/currencies/convert/
        """
        url = "/payments/currencies/convert/"
        response = await self._client.post(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_crypto_retrieve(self) -> Currency:
        """
        Get only cryptocurrencies. GET /api/currencies/crypto/
        """
        url = "/payments/currencies/crypto/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_fiat_retrieve(self) -> Currency:
        """
        Get only fiat currencies. GET /api/currencies/fiat/
        """
        url = "/payments/currencies/fiat/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_health_retrieve(self) -> Currency:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/currencies/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_rates_retrieve(self, base_currency: str, currencies: str) -> Currency:
        """
        Get exchange rates

        Get current exchange rates for specified currencies
        """
        url = "/payments/currencies/rates/"
        response = await self._client.get(url, params={"base_currency": base_currency, "currencies": currencies})
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_stable_retrieve(self) -> Currency:
        """
        Get only stablecoins. GET /api/currencies/stable/
        """
        url = "/payments/currencies/stable/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_stats_retrieve(self) -> Currency:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/currencies/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def currencies_supported_retrieve(self, currency_type: str | None = None, provider: str | None = None) -> Currency:
        """
        Get supported currencies

        Get list of supported currencies from payment providers
        """
        url = "/payments/currencies/supported/"
        response = await self._client.get(url, params={"currency_type": currency_type if currency_type is not None else None, "provider": provider if provider is not None else None})
        response.raise_for_status()
        return Currency.model_validate(response.json())


    async def endpoint_groups_list(self, is_enabled: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedEndpointGroupList]:
        """
        Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
        endpoint group information.
        """
        url = "/payments/endpoint-groups/"
        response = await self._client.get(url, params={"is_enabled": is_enabled if is_enabled is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedEndpointGroupList.model_validate(item) for item in data.get("results", [])]


    async def endpoint_groups_retrieve(self, id: int) -> EndpointGroup:
        """
        Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
        endpoint group information.
        """
        url = f"/payments/endpoint-groups/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    async def endpoint_groups_available_retrieve(self) -> EndpointGroup:
        """
        Get available endpoint groups for subscription. GET
        /api/endpoint-groups/available/
        """
        url = "/payments/endpoint-groups/available/"
        response = await self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    async def endpoint_groups_health_retrieve(self) -> EndpointGroup:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/endpoint-groups/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    async def endpoint_groups_stats_retrieve(self) -> EndpointGroup:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/endpoint-groups/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return EndpointGroup.model_validate(response.json())


    async def health_retrieve(self) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def networks_list(self, is_active: bool | None = None, native_currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedNetworkList]:
        """
        Network ViewSet: /api/networks/ Read-only access to blockchain network
        information.
        """
        url = "/payments/networks/"
        response = await self._client.get(url, params={"is_active": is_active if is_active is not None else None, "native_currency__code": native_currency__code if native_currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedNetworkList.model_validate(item) for item in data.get("results", [])]


    async def networks_retrieve(self, id: int) -> Network:
        """
        Network ViewSet: /api/networks/ Read-only access to blockchain network
        information.
        """
        url = f"/payments/networks/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    async def networks_by_currency_retrieve(self) -> Network:
        """
        Get networks grouped by currency. GET /api/networks/by_currency/
        """
        url = "/payments/networks/by_currency/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    async def networks_health_retrieve(self) -> Network:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/networks/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    async def networks_stats_retrieve(self) -> Network:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/networks/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Network.model_validate(response.json())


    async def overview_dashboard_api_keys_overview_retrieve(self) -> APIKeysOverview:
        """
        API Keys Overview

        Get API keys overview
        """
        url = "/payments/overview/dashboard/api_keys_overview/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeysOverview.model_validate(response.json())


    async def overview_dashboard_balance_overview_retrieve(self) -> BalanceOverview:
        """
        Balance Overview

        Get user balance overview
        """
        url = "/payments/overview/dashboard/balance_overview/"
        response = await self._client.get(url)
        response.raise_for_status()
        return BalanceOverview.model_validate(response.json())


    async def overview_dashboard_chart_data_retrieve(self, period: str | None = None) -> PaymentsChartResponse:
        """
        Payments Chart Data

        Get chart data for payments visualization
        """
        url = "/payments/overview/dashboard/chart_data/"
        response = await self._client.get(url, params={"period": period if period is not None else None})
        response.raise_for_status()
        return PaymentsChartResponse.model_validate(response.json())


    async def overview_dashboard_metrics_retrieve(self) -> PaymentsMetrics:
        """
        Payments Dashboard Metrics

        Get payments dashboard metrics including balance, subscriptions, API
        keys, and payments
        """
        url = "/payments/overview/dashboard/metrics/"
        response = await self._client.get(url)
        response.raise_for_status()
        return PaymentsMetrics.model_validate(response.json())


    async def overview_dashboard_overview_retrieve(self) -> PaymentsDashboardOverview:
        """
        Payments Dashboard Overview

        Get complete payments dashboard overview with metrics, recent payments,
        and analytics
        """
        url = "/payments/overview/dashboard/overview/"
        response = await self._client.get(url)
        response.raise_for_status()
        return PaymentsDashboardOverview.model_validate(response.json())


    async def overview_dashboard_payment_analytics_retrieve(self, limit: int | None = None) -> PaymentAnalyticsResponse:
        """
        Payment Analytics

        Get analytics for payments by currency and provider
        """
        url = "/payments/overview/dashboard/payment_analytics/"
        response = await self._client.get(url, params={"limit": limit if limit is not None else None})
        response.raise_for_status()
        return PaymentAnalyticsResponse.model_validate(response.json())


    async def overview_dashboard_recent_payments_list(self, limit: int | None = None, page: int | None = None, page_size: int | None = None) -> list[PaginatedRecentPaymentList]:
        """
        Recent Payments

        Get recent payments for the user
        """
        url = "/payments/overview/dashboard/recent_payments/"
        response = await self._client.get(url, params={"limit": limit if limit is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedRecentPaymentList.model_validate(item) for item in data.get("results", [])]


    async def overview_dashboard_recent_transactions_list(self, limit: int | None = None, page: int | None = None, page_size: int | None = None) -> list[PaginatedRecentTransactionList]:
        """
        Recent Transactions

        Get recent balance transactions for the user
        """
        url = "/payments/overview/dashboard/recent_transactions/"
        response = await self._client.get(url, params={"limit": limit if limit is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedRecentTransactionList.model_validate(item) for item in data.get("results", [])]


    async def overview_dashboard_subscription_overview_retrieve(self) -> SubscriptionOverview:
        """
        Subscription Overview

        Get current subscription overview
        """
        url = "/payments/overview/dashboard/subscription_overview/"
        response = await self._client.get(url)
        response.raise_for_status()
        return SubscriptionOverview.model_validate(response.json())


    async def payments_list(self, currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None, status: str | None = None, user: int | None = None) -> list[PaginatedPaymentListList]:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = "/payments/payments/"
        response = await self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPaymentListList.model_validate(item) for item in data.get("results", [])]


    async def payments_create(self, data: PaymentCreateRequest) -> PaymentCreate:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = "/payments/payments/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    async def payments_retrieve(self, id: str) -> Payment:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/payments/payments/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_update(self, id: str, data: PaymentRequest) -> Payment:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/payments/payments/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_partial_update(self, id: str, data: PatchedPaymentRequest | None = None) -> Payment:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/payments/payments/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_destroy(self, id: str) -> None:
        """
        Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
        all payments with filtering and stats.
        """
        url = f"/payments/payments/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def payments_cancel_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Cancel payment. POST /api/v1/payments/{id}/cancel/
        """
        url = f"/payments/payments/{id}/cancel/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_check_status_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Check payment status with provider. POST
        /api/v1/payments/{id}/check_status/
        """
        url = f"/payments/payments/{id}/check_status/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_analytics_retrieve(self) -> Payment:
        """
        Get payment analytics. GET /api/v1/payments/analytics/?days=30
        """
        url = "/payments/payments/analytics/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_by_provider_retrieve(self) -> Payment:
        """
        Get payments grouped by provider. GET /api/v1/payments/by_provider/
        """
        url = "/payments/payments/by_provider/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_create_create(self, data: PaymentCreateRequest) -> PaymentCreate:
        """
        Standalone payment creation endpoint: /api/v1/payments/create/
        Simplified endpoint for payment creation without full ViewSet overhead.
        """
        url = "/payments/payments/create/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    async def payments_health_retrieve(self) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/payments/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_stats_retrieve(self) -> Payment:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/payments/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def payments_status_retrieve(self, id: str) -> Payment:
        """
        Standalone payment status endpoint: /api/v1/payments/{id}/status/ Quick
        status check without full ViewSet overhead.
        """
        url = f"/payments/payments/status/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def provider_currencies_list(self, currency__code: str | None = None, is_enabled: bool | None = None, network__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None) -> list[PaginatedProviderCurrencyList]:
        """
        Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
        provider-specific currency information.
        """
        url = "/payments/provider-currencies/"
        response = await self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "is_enabled": is_enabled if is_enabled is not None else None, "network__code": network__code if network__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedProviderCurrencyList.model_validate(item) for item in data.get("results", [])]


    async def provider_currencies_retrieve(self, id: int) -> ProviderCurrency:
        """
        Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
        provider-specific currency information.
        """
        url = f"/payments/provider-currencies/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    async def provider_currencies_by_provider_retrieve(self) -> ProviderCurrency:
        """
        Get provider currencies grouped by provider. GET
        /api/provider-currencies/by_provider/
        """
        url = "/payments/provider-currencies/by_provider/"
        response = await self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    async def provider_currencies_health_retrieve(self) -> ProviderCurrency:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/provider-currencies/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    async def provider_currencies_limits_retrieve(self) -> ProviderCurrency:
        """
        Get currency limits by provider. GET
        /api/provider-currencies/limits/?provider=nowpayments
        """
        url = "/payments/provider-currencies/limits/"
        response = await self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    async def provider_currencies_stats_retrieve(self) -> ProviderCurrency:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/provider-currencies/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return ProviderCurrency.model_validate(response.json())


    async def subscriptions_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None, tier: str | None = None, user: int | None = None) -> list[PaginatedSubscriptionListList]:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = "/payments/subscriptions/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "tier": tier if tier is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedSubscriptionListList.model_validate(item) for item in data.get("results", [])]


    async def subscriptions_create(self, data: SubscriptionCreateRequest) -> SubscriptionCreate:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = "/payments/subscriptions/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return SubscriptionCreate.model_validate(response.json())


    async def subscriptions_retrieve(self, id: str) -> Subscription:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/payments/subscriptions/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_update(self, id: str, data: SubscriptionRequest) -> Subscription:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/payments/subscriptions/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_partial_update(self, id: str, data: PatchedSubscriptionRequest | None = None) -> Subscription:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/payments/subscriptions/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_destroy(self, id: str) -> None:
        """
        Global subscription ViewSet: /api/subscriptions/ Provides admin-level
        access to all subscriptions with filtering and stats.
        """
        url = f"/payments/subscriptions/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def subscriptions_increment_usage_create(self, id: str, data: SubscriptionRequest) -> Subscription:
        """
        Increment subscription usage. POST
        /api/subscriptions/{id}/increment_usage/
        """
        url = f"/payments/subscriptions/{id}/increment_usage/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_update_status_create(self, id: str, data: SubscriptionRequest) -> Subscription:
        """
        Update subscription status. POST /api/subscriptions/{id}/update_status/
        """
        url = f"/payments/subscriptions/{id}/update_status/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_analytics_retrieve(self) -> Subscription:
        """
        Get subscription analytics. GET /api/subscriptions/analytics/?days=30
        """
        url = "/payments/subscriptions/analytics/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_by_status_retrieve(self) -> Subscription:
        """
        Get subscriptions grouped by status. GET /api/subscriptions/by_status/
        """
        url = "/payments/subscriptions/by_status/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_by_tier_retrieve(self) -> Subscription:
        """
        Get subscriptions grouped by tier. GET /api/subscriptions/by_tier/
        """
        url = "/payments/subscriptions/by_tier/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_health_retrieve(self) -> Subscription:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/subscriptions/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def subscriptions_stats_retrieve(self) -> Subscription:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/subscriptions/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def tariffs_list(self, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedTariffList]:
        """
        Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
        subscription selection.
        """
        url = "/payments/tariffs/"
        response = await self._client.get(url, params={"is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedTariffList.model_validate(item) for item in data.get("results", [])]


    async def tariffs_retrieve(self, id: int) -> Tariff:
        """
        Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
        subscription selection.
        """
        url = f"/payments/tariffs/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    async def tariffs_endpoint_groups_retrieve(self, id: int) -> Tariff:
        """
        Get endpoint groups for specific tariff. GET
        /api/tariffs/{id}/endpoint_groups/
        """
        url = f"/payments/tariffs/{id}/endpoint_groups/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    async def tariffs_free_retrieve(self) -> Tariff:
        """
        Get free tariffs. GET /api/tariffs/free/
        """
        url = "/payments/tariffs/free/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    async def tariffs_health_retrieve(self) -> Tariff:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/tariffs/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    async def tariffs_paid_retrieve(self) -> Tariff:
        """
        Get paid tariffs. GET /api/tariffs/paid/
        """
        url = "/payments/tariffs/paid/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    async def tariffs_stats_retrieve(self) -> Tariff:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/tariffs/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Tariff.model_validate(response.json())


    async def transactions_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, payment_id: str | None = None, search: str | None = None, transaction_type: str | None = None, user: int | None = None) -> list[PaginatedTransactionList]:
        """
        Transaction ViewSet: /api/transactions/ Read-only access to transaction
        history with filtering.
        """
        url = "/payments/transactions/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "payment_id": payment_id if payment_id is not None else None, "search": search if search is not None else None, "transaction_type": transaction_type if transaction_type is not None else None, "user": user if user is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedTransactionList.model_validate(item) for item in data.get("results", [])]


    async def transactions_retrieve(self, id: str) -> Transaction:
        """
        Transaction ViewSet: /api/transactions/ Read-only access to transaction
        history with filtering.
        """
        url = f"/payments/transactions/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    async def transactions_by_type_retrieve(self) -> Transaction:
        """
        Get transactions grouped by type. GET /api/transactions/by_type/
        """
        url = "/payments/transactions/by_type/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    async def transactions_health_retrieve(self) -> Transaction:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/transactions/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    async def transactions_recent_retrieve(self) -> Transaction:
        """
        Get recent transactions. GET /api/transactions/recent/?limit=10
        """
        url = "/payments/transactions/recent/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    async def transactions_stats_retrieve(self) -> Transaction:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/transactions/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Transaction.model_validate(response.json())


    async def users_list(self, currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None, status: str | None = None) -> list[PaginatedPaymentListList]:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = "/payments/users/"
        response = await self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPaymentListList.model_validate(item) for item in data.get("results", [])]


    async def users_create(self, data: PaymentCreateRequest) -> PaymentCreate:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = "/payments/users/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    async def users_retrieve(self, id: str) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_update(self, id: str, data: PaymentRequest) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_partial_update(self, id: str, data: PatchedPaymentRequest | None = None) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_destroy(self, id: str) -> None:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def users_cancel_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
        """
        url = f"/payments/users/{id}/cancel/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_check_status_create(self, id: str, data: PaymentRequest) -> Payment:
        """
        Check payment status with provider. POST
        /api/v1/users/{user_id}/payments/{id}/check_status/
        """
        url = f"/payments/users/{id}/check_status/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_api_keys_list(self, user_pk: int, is_active: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedAPIKeyListList]:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/api-keys/"
        response = await self._client.get(url, params={"is_active": is_active if is_active is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedAPIKeyListList.model_validate(item) for item in data.get("results", [])]


    async def users_api_keys_create(self, user_pk: int, data: APIKeyCreateRequest) -> APIKeyCreate:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/api-keys/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIKeyCreate.model_validate(response.json())


    async def users_api_keys_retrieve(self, id: str, user_pk: int) -> APIKeyDetail:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/api-keys/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def users_api_keys_update(self, id: str, user_pk: int, data: APIKeyUpdateRequest) -> APIKeyUpdate:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/api-keys/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    async def users_api_keys_partial_update(self, id: str, user_pk: int, data: PatchedAPIKeyUpdateRequest | None = None) -> APIKeyUpdate:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/api-keys/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return APIKeyUpdate.model_validate(response.json())


    async def users_api_keys_destroy(self, id: str, user_pk: int) -> None:
        """
        User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
        user-scoped access to API keys with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/api-keys/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def users_api_keys_perform_action_create(self, id: str, user_pk: int) -> APIKeyDetail:
        """
        Perform action on API key. POST
        /api/users/{user_id}/api-keys/{id}/perform_action/
        """
        url = f"/payments/users/{user_pk}/api-keys/{id}/perform_action/"
        response = await self._client.post(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def users_api_keys_active_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Get user's active API keys. GET /api/users/{user_id}/api-keys/active/
        """
        url = f"/payments/users/{user_pk}/api-keys/active/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def users_api_keys_health_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = f"/payments/users/{user_pk}/api-keys/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def users_api_keys_stats_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = f"/payments/users/{user_pk}/api-keys/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def users_api_keys_summary_retrieve(self, user_pk: int) -> APIKeyDetail:
        """
        Get user API key summary. GET /api/users/{user_id}/api-keys/summary/
        """
        url = f"/payments/users/{user_pk}/api-keys/summary/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIKeyDetail.model_validate(response.json())


    async def users_payments_list(self, user_pk: int, currency__code: str | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, provider: str | None = None, search: str | None = None, status: str | None = None) -> list[PaginatedPaymentListList]:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/payments/"
        response = await self._client.get(url, params={"currency__code": currency__code if currency__code is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "provider": provider if provider is not None else None, "search": search if search is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPaymentListList.model_validate(item) for item in data.get("results", [])]


    async def users_payments_create(self, user_pk: int, data: PaymentCreateRequest) -> PaymentCreate:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/payments/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return PaymentCreate.model_validate(response.json())


    async def users_payments_retrieve(self, id: str, user_pk: int) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/payments/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_payments_update(self, id: str, user_pk: int, data: PaymentRequest) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/payments/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_payments_partial_update(self, id: str, user_pk: int, data: PatchedPaymentRequest | None = None) -> Payment:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/payments/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_payments_destroy(self, id: str, user_pk: int) -> None:
        """
        User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
        Provides user-scoped access to payments with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/payments/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def users_payments_cancel_create(self, id: str, user_pk: int, data: PaymentRequest) -> Payment:
        """
        Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
        """
        url = f"/payments/users/{user_pk}/payments/{id}/cancel/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_payments_check_status_create(self, id: str, user_pk: int, data: PaymentRequest) -> Payment:
        """
        Check payment status with provider. POST
        /api/v1/users/{user_id}/payments/{id}/check_status/
        """
        url = f"/payments/users/{user_pk}/payments/{id}/check_status/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_payments_health_retrieve(self, user_pk: int) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = f"/payments/users/{user_pk}/payments/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_payments_stats_retrieve(self, user_pk: int) -> Payment:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = f"/payments/users/{user_pk}/payments/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_payments_summary_retrieve(self, user_pk: int) -> Payment:
        """
        Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
        """
        url = f"/payments/users/{user_pk}/payments/summary/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_subscriptions_list(self, user_pk: int, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None, tier: str | None = None) -> list[PaginatedSubscriptionListList]:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/subscriptions/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "tier": tier if tier is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedSubscriptionListList.model_validate(item) for item in data.get("results", [])]


    async def users_subscriptions_create(self, user_pk: int, data: SubscriptionCreateRequest) -> SubscriptionCreate:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/subscriptions/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return SubscriptionCreate.model_validate(response.json())


    async def users_subscriptions_retrieve(self, id: str, user_pk: int) -> Subscription:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/subscriptions/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_update(self, id: str, user_pk: int, data: SubscriptionRequest) -> Subscription:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/subscriptions/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_partial_update(self, id: str, user_pk: int, data: PatchedSubscriptionRequest | None = None) -> Subscription:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/subscriptions/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_destroy(self, id: str, user_pk: int) -> None:
        """
        User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
        Provides user-scoped access to subscriptions with full CRUD operations.
        """
        url = f"/payments/users/{user_pk}/subscriptions/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def users_subscriptions_increment_usage_create(self, id: str, user_pk: int, data: SubscriptionRequest) -> Subscription:
        """
        Increment subscription usage. POST
        /api/users/{user_id}/subscriptions/{id}/increment_usage/
        """
        url = f"/payments/users/{user_pk}/subscriptions/{id}/increment_usage/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_update_status_create(self, id: str, user_pk: int, data: SubscriptionRequest) -> Subscription:
        """
        Update subscription status. POST
        /api/users/{user_id}/subscriptions/{id}/update_status/
        """
        url = f"/payments/users/{user_pk}/subscriptions/{id}/update_status/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_active_retrieve(self, user_pk: int) -> Subscription:
        """
        Get user's active subscription. GET
        /api/users/{user_id}/subscriptions/active/
        """
        url = f"/payments/users/{user_pk}/subscriptions/active/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_health_retrieve(self, user_pk: int) -> Subscription:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = f"/payments/users/{user_pk}/subscriptions/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_stats_retrieve(self, user_pk: int) -> Subscription:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = f"/payments/users/{user_pk}/subscriptions/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_subscriptions_summary_retrieve(self, user_pk: int) -> Subscription:
        """
        Get user subscription summary. GET
        /api/users/{user_id}/subscriptions/summary/
        """
        url = f"/payments/users/{user_pk}/subscriptions/summary/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Subscription.model_validate(response.json())


    async def users_health_retrieve(self) -> Payment:
        """
        Health check for the ViewSet and related services. Returns service
        status and basic metrics.
        """
        url = "/payments/users/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_stats_retrieve(self) -> Payment:
        """
        Get statistics for the current queryset. Returns counts, aggregates, and
        breakdowns.
        """
        url = "/payments/users/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


    async def users_summary_retrieve(self) -> Payment:
        """
        Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
        """
        url = "/payments/users/summary/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Payment.model_validate(response.json())


