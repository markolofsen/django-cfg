import * as Models from "./models";


/**
 * API endpoints for Payments.
 */
export class CfgPaymentsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
 * all API keys with filtering and stats.
 */
async apiKeysList(is_active?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, user?: number | null): Promise<Models.PaginatedAPIKeyListList[]> {
  const response = await this.client.request<Models.PaginatedAPIKeyListList[]>('GET', "/payments/api-keys/", { params: { is_active, ordering, page, page_size, search, user } });
  return (response as any).results || [];
}

  /**
 * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
 * all API keys with filtering and stats.
 */
async apiKeysCreate(data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
  const response = await this.client.request<Models.APIKeyCreate>('POST', "/payments/api-keys/", { body: data });
  return response;
}

  /**
 * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
 * all API keys with filtering and stats.
 */
async apiKeysRetrieve(id: string): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', `/payments/api-keys/${id}/`);
  return response;
}

  /**
 * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
 * all API keys with filtering and stats.
 */
async apiKeysUpdate(id: string, data: Models.APIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
  const response = await this.client.request<Models.APIKeyUpdate>('PUT', `/payments/api-keys/${id}/`, { body: data });
  return response;
}

  /**
 * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
 * all API keys with filtering and stats.
 */
async apiKeysPartialUpdate(id: string, data?: Models.PatchedAPIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
  const response = await this.client.request<Models.APIKeyUpdate>('PATCH', `/payments/api-keys/${id}/`, { body: data });
  return response;
}

  /**
 * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
 * all API keys with filtering and stats.
 */
async apiKeysDestroy(id: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/payments/api-keys/${id}/`);
  return;
}

  /**
 * Perform action on API key. POST /api/api-keys/{id}/perform_action/
 */
async apiKeysPerformActionCreate(id: string): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('POST', `/payments/api-keys/${id}/perform_action/`);
  return response;
}

  /**
 * Get API key analytics. GET /api/api-keys/analytics/?days=30
 */
async apiKeysAnalyticsRetrieve(): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', "/payments/api-keys/analytics/");
  return response;
}

  /**
 * Get API keys grouped by user. GET /api/api-keys/by_user/
 */
async apiKeysByUserRetrieve(): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', "/payments/api-keys/by_user/");
  return response;
}

  /**
 * Standalone API key creation endpoint: /api/api-keys/create/ Simplified
 * endpoint for API key creation.
 */
async apiKeysCreateCreate(data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
  const response = await this.client.request<Models.APIKeyCreate>('POST', "/payments/api-keys/create/", { body: data });
  return response;
}

  /**
 * Get API keys expiring soon. GET /api/api-keys/expiring_soon/?days=7
 */
async apiKeysExpiringSoonRetrieve(): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', "/payments/api-keys/expiring_soon/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async apiKeysHealthRetrieve(): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', "/payments/api-keys/health/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async apiKeysStatsRetrieve(): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', "/payments/api-keys/stats/");
  return response;
}

  /**
 * Validate API Key (Standalone)
 * 
 * Standalone endpoint to validate an API key and return key information
 */
async apiKeysValidateCreate(data: Models.APIKeyValidationRequest): Promise<Models.APIKeyValidationResponse> {
  const response = await this.client.request<Models.APIKeyValidationResponse>('POST', "/payments/api-keys/validate/", { body: data });
  return response;
}

  /**
 * Validate API Key
 * 
 * Validate an API key and return key information
 */
async apiKeysValidateKeyCreate(data: Models.APIKeyValidationRequest): Promise<Models.APIKeyValidationResponse> {
  const response = await this.client.request<Models.APIKeyValidationResponse>('POST', "/payments/api-keys/validate_key/", { body: data });
  return response;
}

  /**
 * User balance ViewSet: /api/balances/ Read-only access to user balances
 * with statistics.
 */
async balancesList(ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, user?: number | null): Promise<Models.PaginatedUserBalanceList[]> {
  const response = await this.client.request<Models.PaginatedUserBalanceList[]>('GET', "/payments/balances/", { params: { ordering, page, page_size, search, user } });
  return (response as any).results || [];
}

  /**
 * User balance ViewSet: /api/balances/ Read-only access to user balances
 * with statistics.
 */
async balancesRetrieve(id: number): Promise<Models.UserBalance> {
  const response = await this.client.request<Models.UserBalance>('GET', `/payments/balances/${id}/`);
  return response;
}

  /**
 * Get balance analytics. GET /api/balances/analytics/?days=30
 */
async balancesAnalyticsRetrieve(): Promise<Models.UserBalance> {
  const response = await this.client.request<Models.UserBalance>('GET', "/payments/balances/analytics/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async balancesHealthRetrieve(): Promise<Models.UserBalance> {
  const response = await this.client.request<Models.UserBalance>('GET', "/payments/balances/health/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async balancesStatsRetrieve(): Promise<Models.UserBalance> {
  const response = await this.client.request<Models.UserBalance>('GET', "/payments/balances/stats/");
  return response;
}

  /**
 * Get balance summary for all users. GET /api/balances/summary/
 */
async balancesSummaryRetrieve(): Promise<Models.UserBalance> {
  const response = await this.client.request<Models.UserBalance>('GET', "/payments/balances/summary/");
  return response;
}

  /**
 * Currency ViewSet: /api/currencies/ Read-only access to currency
 * information with conversion capabilities.
 */
async currenciesList(currency_type?: string | null, is_active?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedCurrencyListList[]> {
  const response = await this.client.request<Models.PaginatedCurrencyListList[]>('GET', "/payments/currencies/", { params: { currency_type, is_active, ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * Disable create action.
 */
async currenciesCreate(): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('POST', "/payments/currencies/");
  return response;
}

  /**
 * Currency ViewSet: /api/currencies/ Read-only access to currency
 * information with conversion capabilities.
 */
async currenciesRetrieve(id: number): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', `/payments/currencies/${id}/`);
  return response;
}

  /**
 * Get networks for specific currency. GET /api/currencies/{id}/networks/
 */
async currenciesNetworksRetrieve(id: number): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', `/payments/currencies/${id}/networks/`);
  return response;
}

  /**
 * Get providers supporting specific currency. GET
 * /api/currencies/{id}/providers/
 */
async currenciesProvidersRetrieve(id: number): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', `/payments/currencies/${id}/providers/`);
  return response;
}

  /**
 * Convert between currencies. POST /api/currencies/convert/
 */
async currenciesConvertCreate(): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('POST', "/payments/currencies/convert/");
  return response;
}

  /**
 * Get only cryptocurrencies. GET /api/currencies/crypto/
 */
async currenciesCryptoRetrieve(): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', "/payments/currencies/crypto/");
  return response;
}

  /**
 * Get only fiat currencies. GET /api/currencies/fiat/
 */
async currenciesFiatRetrieve(): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', "/payments/currencies/fiat/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async currenciesHealthRetrieve(): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', "/payments/currencies/health/");
  return response;
}

  /**
 * Get exchange rates
 * 
 * Get current exchange rates for specified currencies
 */
async currenciesRatesRetrieve(base_currency: string, currencies: string): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', "/payments/currencies/rates/", { params: { base_currency, currencies } });
  return response;
}

  /**
 * Get only stablecoins. GET /api/currencies/stable/
 */
async currenciesStableRetrieve(): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', "/payments/currencies/stable/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async currenciesStatsRetrieve(): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', "/payments/currencies/stats/");
  return response;
}

  /**
 * Get supported currencies
 * 
 * Get list of supported currencies from payment providers
 */
async currenciesSupportedRetrieve(currency_type?: string | null, provider?: string | null): Promise<Models.Currency> {
  const response = await this.client.request<Models.Currency>('GET', "/payments/currencies/supported/", { params: { currency_type, provider } });
  return response;
}

  /**
 * Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
 * endpoint group information.
 */
async endpointGroupsList(is_enabled?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedEndpointGroupList[]> {
  const response = await this.client.request<Models.PaginatedEndpointGroupList[]>('GET', "/payments/endpoint-groups/", { params: { is_enabled, ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
 * endpoint group information.
 */
async endpointGroupsRetrieve(id: number): Promise<Models.EndpointGroup> {
  const response = await this.client.request<Models.EndpointGroup>('GET', `/payments/endpoint-groups/${id}/`);
  return response;
}

  /**
 * Get available endpoint groups for subscription. GET
 * /api/endpoint-groups/available/
 */
async endpointGroupsAvailableRetrieve(): Promise<Models.EndpointGroup> {
  const response = await this.client.request<Models.EndpointGroup>('GET', "/payments/endpoint-groups/available/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async endpointGroupsHealthRetrieve(): Promise<Models.EndpointGroup> {
  const response = await this.client.request<Models.EndpointGroup>('GET', "/payments/endpoint-groups/health/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async endpointGroupsStatsRetrieve(): Promise<Models.EndpointGroup> {
  const response = await this.client.request<Models.EndpointGroup>('GET', "/payments/endpoint-groups/stats/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async healthRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/health/");
  return response;
}

  /**
 * Network ViewSet: /api/networks/ Read-only access to blockchain network
 * information.
 */
async networksList(is_active?: boolean | null, native_currency__code?: string | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedNetworkList[]> {
  const response = await this.client.request<Models.PaginatedNetworkList[]>('GET', "/payments/networks/", { params: { is_active, native_currency__code, ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * Network ViewSet: /api/networks/ Read-only access to blockchain network
 * information.
 */
async networksRetrieve(id: number): Promise<Models.Network> {
  const response = await this.client.request<Models.Network>('GET', `/payments/networks/${id}/`);
  return response;
}

  /**
 * Get networks grouped by currency. GET /api/networks/by_currency/
 */
async networksByCurrencyRetrieve(): Promise<Models.Network> {
  const response = await this.client.request<Models.Network>('GET', "/payments/networks/by_currency/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async networksHealthRetrieve(): Promise<Models.Network> {
  const response = await this.client.request<Models.Network>('GET', "/payments/networks/health/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async networksStatsRetrieve(): Promise<Models.Network> {
  const response = await this.client.request<Models.Network>('GET', "/payments/networks/stats/");
  return response;
}

  /**
 * API Keys Overview
 * 
 * Get API keys overview
 */
async overviewDashboardApiKeysOverviewRetrieve(): Promise<Models.APIKeysOverview> {
  const response = await this.client.request<Models.APIKeysOverview>('GET', "/payments/overview/dashboard/api_keys_overview/");
  return response;
}

  /**
 * Balance Overview
 * 
 * Get user balance overview
 */
async overviewDashboardBalanceOverviewRetrieve(): Promise<Models.BalanceOverview> {
  const response = await this.client.request<Models.BalanceOverview>('GET', "/payments/overview/dashboard/balance_overview/");
  return response;
}

  /**
 * Payments Chart Data
 * 
 * Get chart data for payments visualization
 */
async overviewDashboardChartDataRetrieve(period?: string | null): Promise<Models.PaymentsChartResponse> {
  const response = await this.client.request<Models.PaymentsChartResponse>('GET', "/payments/overview/dashboard/chart_data/", { params: { period } });
  return response;
}

  /**
 * Payments Dashboard Metrics
 * 
 * Get payments dashboard metrics including balance, subscriptions, API
 * keys, and payments
 */
async overviewDashboardMetricsRetrieve(): Promise<Models.PaymentsMetrics> {
  const response = await this.client.request<Models.PaymentsMetrics>('GET', "/payments/overview/dashboard/metrics/");
  return response;
}

  /**
 * Payments Dashboard Overview
 * 
 * Get complete payments dashboard overview with metrics, recent payments,
 * and analytics
 */
async overviewDashboardOverviewRetrieve(): Promise<Models.PaymentsDashboardOverview> {
  const response = await this.client.request<Models.PaymentsDashboardOverview>('GET', "/payments/overview/dashboard/overview/");
  return response;
}

  /**
 * Payment Analytics
 * 
 * Get analytics for payments by currency and provider
 */
async overviewDashboardPaymentAnalyticsRetrieve(limit?: number | null): Promise<Models.PaymentAnalyticsResponse> {
  const response = await this.client.request<Models.PaymentAnalyticsResponse>('GET', "/payments/overview/dashboard/payment_analytics/", { params: { limit } });
  return response;
}

  /**
 * Recent Payments
 * 
 * Get recent payments for the user
 */
async overviewDashboardRecentPaymentsList(limit?: number | null, page?: number | null, page_size?: number | null): Promise<Models.PaginatedRecentPaymentList[]> {
  const response = await this.client.request<Models.PaginatedRecentPaymentList[]>('GET', "/payments/overview/dashboard/recent_payments/", { params: { limit, page, page_size } });
  return (response as any).results || [];
}

  /**
 * Recent Transactions
 * 
 * Get recent balance transactions for the user
 */
async overviewDashboardRecentTransactionsList(limit?: number | null, page?: number | null, page_size?: number | null): Promise<Models.PaginatedRecentTransactionList[]> {
  const response = await this.client.request<Models.PaginatedRecentTransactionList[]>('GET', "/payments/overview/dashboard/recent_transactions/", { params: { limit, page, page_size } });
  return (response as any).results || [];
}

  /**
 * Subscription Overview
 * 
 * Get current subscription overview
 */
async overviewDashboardSubscriptionOverviewRetrieve(): Promise<Models.SubscriptionOverview> {
  const response = await this.client.request<Models.SubscriptionOverview>('GET', "/payments/overview/dashboard/subscription_overview/");
  return response;
}

  /**
 * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
 * all payments with filtering and stats.
 */
async paymentsList(currency__code?: string | null, ordering?: string | null, page?: number | null, page_size?: number | null, provider?: string | null, search?: string | null, status?: string | null, user?: number | null): Promise<Models.PaginatedPaymentListList[]> {
  const response = await this.client.request<Models.PaginatedPaymentListList[]>('GET', "/payments/payments/", { params: { currency__code, ordering, page, page_size, provider, search, status, user } });
  return (response as any).results || [];
}

  /**
 * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
 * all payments with filtering and stats.
 */
async paymentsCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
  const response = await this.client.request<Models.PaymentCreate>('POST', "/payments/payments/", { body: data });
  return response;
}

  /**
 * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
 * all payments with filtering and stats.
 */
async paymentsRetrieve(id: string): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', `/payments/payments/${id}/`);
  return response;
}

  /**
 * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
 * all payments with filtering and stats.
 */
async paymentsUpdate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('PUT', `/payments/payments/${id}/`, { body: data });
  return response;
}

  /**
 * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
 * all payments with filtering and stats.
 */
async paymentsPartialUpdate(id: string, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('PATCH', `/payments/payments/${id}/`, { body: data });
  return response;
}

  /**
 * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
 * all payments with filtering and stats.
 */
async paymentsDestroy(id: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/payments/payments/${id}/`);
  return;
}

  /**
 * Cancel payment. POST /api/v1/payments/{id}/cancel/
 */
async paymentsCancelCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('POST', `/payments/payments/${id}/cancel/`, { body: data });
  return response;
}

  /**
 * Check payment status with provider. POST
 * /api/v1/payments/{id}/check_status/
 */
async paymentsCheckStatusCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('POST', `/payments/payments/${id}/check_status/`, { body: data });
  return response;
}

  /**
 * Get payment analytics. GET /api/v1/payments/analytics/?days=30
 */
async paymentsAnalyticsRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/payments/analytics/");
  return response;
}

  /**
 * Get payments grouped by provider. GET /api/v1/payments/by_provider/
 */
async paymentsByProviderRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/payments/by_provider/");
  return response;
}

  /**
 * Standalone payment creation endpoint: /api/v1/payments/create/
 * Simplified endpoint for payment creation without full ViewSet overhead.
 */
async paymentsCreateCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
  const response = await this.client.request<Models.PaymentCreate>('POST', "/payments/payments/create/", { body: data });
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async paymentsHealthRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/payments/health/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async paymentsStatsRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/payments/stats/");
  return response;
}

  /**
 * Standalone payment status endpoint: /api/v1/payments/{id}/status/ Quick
 * status check without full ViewSet overhead.
 */
async paymentsStatusRetrieve(id: string): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', `/payments/payments/status/${id}/`);
  return response;
}

  /**
 * Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
 * provider-specific currency information.
 */
async providerCurrenciesList(currency__code?: string | null, is_enabled?: boolean | null, network__code?: string | null, ordering?: string | null, page?: number | null, page_size?: number | null, provider?: string | null, search?: string | null): Promise<Models.PaginatedProviderCurrencyList[]> {
  const response = await this.client.request<Models.PaginatedProviderCurrencyList[]>('GET', "/payments/provider-currencies/", { params: { currency__code, is_enabled, network__code, ordering, page, page_size, provider, search } });
  return (response as any).results || [];
}

  /**
 * Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
 * provider-specific currency information.
 */
async providerCurrenciesRetrieve(id: number): Promise<Models.ProviderCurrency> {
  const response = await this.client.request<Models.ProviderCurrency>('GET', `/payments/provider-currencies/${id}/`);
  return response;
}

  /**
 * Get provider currencies grouped by provider. GET
 * /api/provider-currencies/by_provider/
 */
async providerCurrenciesByProviderRetrieve(): Promise<Models.ProviderCurrency> {
  const response = await this.client.request<Models.ProviderCurrency>('GET', "/payments/provider-currencies/by_provider/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async providerCurrenciesHealthRetrieve(): Promise<Models.ProviderCurrency> {
  const response = await this.client.request<Models.ProviderCurrency>('GET', "/payments/provider-currencies/health/");
  return response;
}

  /**
 * Get currency limits by provider. GET
 * /api/provider-currencies/limits/?provider=nowpayments
 */
async providerCurrenciesLimitsRetrieve(): Promise<Models.ProviderCurrency> {
  const response = await this.client.request<Models.ProviderCurrency>('GET', "/payments/provider-currencies/limits/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async providerCurrenciesStatsRetrieve(): Promise<Models.ProviderCurrency> {
  const response = await this.client.request<Models.ProviderCurrency>('GET', "/payments/provider-currencies/stats/");
  return response;
}

  /**
 * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
 * access to all subscriptions with filtering and stats.
 */
async subscriptionsList(ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, status?: string | null, tier?: string | null, user?: number | null): Promise<Models.PaginatedSubscriptionListList[]> {
  const response = await this.client.request<Models.PaginatedSubscriptionListList[]>('GET', "/payments/subscriptions/", { params: { ordering, page, page_size, search, status, tier, user } });
  return (response as any).results || [];
}

  /**
 * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
 * access to all subscriptions with filtering and stats.
 */
async subscriptionsCreate(data: Models.SubscriptionCreateRequest): Promise<Models.SubscriptionCreate> {
  const response = await this.client.request<Models.SubscriptionCreate>('POST', "/payments/subscriptions/", { body: data });
  return response;
}

  /**
 * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
 * access to all subscriptions with filtering and stats.
 */
async subscriptionsRetrieve(id: string): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', `/payments/subscriptions/${id}/`);
  return response;
}

  /**
 * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
 * access to all subscriptions with filtering and stats.
 */
async subscriptionsUpdate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('PUT', `/payments/subscriptions/${id}/`, { body: data });
  return response;
}

  /**
 * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
 * access to all subscriptions with filtering and stats.
 */
async subscriptionsPartialUpdate(id: string, data?: Models.PatchedSubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('PATCH', `/payments/subscriptions/${id}/`, { body: data });
  return response;
}

  /**
 * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
 * access to all subscriptions with filtering and stats.
 */
async subscriptionsDestroy(id: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/payments/subscriptions/${id}/`);
  return;
}

  /**
 * Increment subscription usage. POST
 * /api/subscriptions/{id}/increment_usage/
 */
async subscriptionsIncrementUsageCreate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('POST', `/payments/subscriptions/${id}/increment_usage/`, { body: data });
  return response;
}

  /**
 * Update subscription status. POST /api/subscriptions/{id}/update_status/
 */
async subscriptionsUpdateStatusCreate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('POST', `/payments/subscriptions/${id}/update_status/`, { body: data });
  return response;
}

  /**
 * Get subscription analytics. GET /api/subscriptions/analytics/?days=30
 */
async subscriptionsAnalyticsRetrieve(): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', "/payments/subscriptions/analytics/");
  return response;
}

  /**
 * Get subscriptions grouped by status. GET /api/subscriptions/by_status/
 */
async subscriptionsByStatusRetrieve(): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', "/payments/subscriptions/by_status/");
  return response;
}

  /**
 * Get subscriptions grouped by tier. GET /api/subscriptions/by_tier/
 */
async subscriptionsByTierRetrieve(): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', "/payments/subscriptions/by_tier/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async subscriptionsHealthRetrieve(): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', "/payments/subscriptions/health/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async subscriptionsStatsRetrieve(): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', "/payments/subscriptions/stats/");
  return response;
}

  /**
 * Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
 * subscription selection.
 */
async tariffsList(is_active?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedTariffList[]> {
  const response = await this.client.request<Models.PaginatedTariffList[]>('GET', "/payments/tariffs/", { params: { is_active, ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
 * subscription selection.
 */
async tariffsRetrieve(id: number): Promise<Models.Tariff> {
  const response = await this.client.request<Models.Tariff>('GET', `/payments/tariffs/${id}/`);
  return response;
}

  /**
 * Get endpoint groups for specific tariff. GET
 * /api/tariffs/{id}/endpoint_groups/
 */
async tariffsEndpointGroupsRetrieve(id: number): Promise<Models.Tariff> {
  const response = await this.client.request<Models.Tariff>('GET', `/payments/tariffs/${id}/endpoint_groups/`);
  return response;
}

  /**
 * Get free tariffs. GET /api/tariffs/free/
 */
async tariffsFreeRetrieve(): Promise<Models.Tariff> {
  const response = await this.client.request<Models.Tariff>('GET', "/payments/tariffs/free/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async tariffsHealthRetrieve(): Promise<Models.Tariff> {
  const response = await this.client.request<Models.Tariff>('GET', "/payments/tariffs/health/");
  return response;
}

  /**
 * Get paid tariffs. GET /api/tariffs/paid/
 */
async tariffsPaidRetrieve(): Promise<Models.Tariff> {
  const response = await this.client.request<Models.Tariff>('GET', "/payments/tariffs/paid/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async tariffsStatsRetrieve(): Promise<Models.Tariff> {
  const response = await this.client.request<Models.Tariff>('GET', "/payments/tariffs/stats/");
  return response;
}

  /**
 * Transaction ViewSet: /api/transactions/ Read-only access to transaction
 * history with filtering.
 */
async transactionsList(ordering?: string | null, page?: number | null, page_size?: number | null, payment_id?: string | null, search?: string | null, transaction_type?: string | null, user?: number | null): Promise<Models.PaginatedTransactionList[]> {
  const response = await this.client.request<Models.PaginatedTransactionList[]>('GET', "/payments/transactions/", { params: { ordering, page, page_size, payment_id, search, transaction_type, user } });
  return (response as any).results || [];
}

  /**
 * Transaction ViewSet: /api/transactions/ Read-only access to transaction
 * history with filtering.
 */
async transactionsRetrieve(id: string): Promise<Models.Transaction> {
  const response = await this.client.request<Models.Transaction>('GET', `/payments/transactions/${id}/`);
  return response;
}

  /**
 * Get transactions grouped by type. GET /api/transactions/by_type/
 */
async transactionsByTypeRetrieve(): Promise<Models.Transaction> {
  const response = await this.client.request<Models.Transaction>('GET', "/payments/transactions/by_type/");
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async transactionsHealthRetrieve(): Promise<Models.Transaction> {
  const response = await this.client.request<Models.Transaction>('GET', "/payments/transactions/health/");
  return response;
}

  /**
 * Get recent transactions. GET /api/transactions/recent/?limit=10
 */
async transactionsRecentRetrieve(): Promise<Models.Transaction> {
  const response = await this.client.request<Models.Transaction>('GET', "/payments/transactions/recent/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async transactionsStatsRetrieve(): Promise<Models.Transaction> {
  const response = await this.client.request<Models.Transaction>('GET', "/payments/transactions/stats/");
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersList(currency__code?: string | null, ordering?: string | null, page?: number | null, page_size?: number | null, provider?: string | null, search?: string | null, status?: string | null): Promise<Models.PaginatedPaymentListList[]> {
  const response = await this.client.request<Models.PaginatedPaymentListList[]>('GET', "/payments/users/", { params: { currency__code, ordering, page, page_size, provider, search, status } });
  return (response as any).results || [];
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
  const response = await this.client.request<Models.PaymentCreate>('POST', "/payments/users/", { body: data });
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersRetrieve(id: string): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', `/payments/users/${id}/`);
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersUpdate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('PUT', `/payments/users/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersPartialUpdate(id: string, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('PATCH', `/payments/users/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersDestroy(id: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/payments/users/${id}/`);
  return;
}

  /**
 * Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
 */
async usersCancelCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('POST', `/payments/users/${id}/cancel/`, { body: data });
  return response;
}

  /**
 * Check payment status with provider. POST
 * /api/v1/users/{user_id}/payments/{id}/check_status/
 */
async usersCheckStatusCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('POST', `/payments/users/${id}/check_status/`, { body: data });
  return response;
}

  /**
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
 * user-scoped access to API keys with full CRUD operations.
 */
async usersApiKeysList(user_pk: number, is_active?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedAPIKeyListList[]> {
  const response = await this.client.request<Models.PaginatedAPIKeyListList[]>('GET', `/payments/users/${user_pk}/api-keys/`, { params: { is_active, ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
 * user-scoped access to API keys with full CRUD operations.
 */
async usersApiKeysCreate(user_pk: number, data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
  const response = await this.client.request<Models.APIKeyCreate>('POST', `/payments/users/${user_pk}/api-keys/`, { body: data });
  return response;
}

  /**
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
 * user-scoped access to API keys with full CRUD operations.
 */
async usersApiKeysRetrieve(id: string, user_pk: number): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', `/payments/users/${user_pk}/api-keys/${id}/`);
  return response;
}

  /**
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
 * user-scoped access to API keys with full CRUD operations.
 */
async usersApiKeysUpdate(id: string, user_pk: number, data: Models.APIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
  const response = await this.client.request<Models.APIKeyUpdate>('PUT', `/payments/users/${user_pk}/api-keys/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
 * user-scoped access to API keys with full CRUD operations.
 */
async usersApiKeysPartialUpdate(id: string, user_pk: number, data?: Models.PatchedAPIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
  const response = await this.client.request<Models.APIKeyUpdate>('PATCH', `/payments/users/${user_pk}/api-keys/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
 * user-scoped access to API keys with full CRUD operations.
 */
async usersApiKeysDestroy(id: string, user_pk: number): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/payments/users/${user_pk}/api-keys/${id}/`);
  return;
}

  /**
 * Perform action on API key. POST
 * /api/users/{user_id}/api-keys/{id}/perform_action/
 */
async usersApiKeysPerformActionCreate(id: string, user_pk: number): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('POST', `/payments/users/${user_pk}/api-keys/${id}/perform_action/`);
  return response;
}

  /**
 * Get user's active API keys. GET /api/users/{user_id}/api-keys/active/
 */
async usersApiKeysActiveRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', `/payments/users/${user_pk}/api-keys/active/`);
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async usersApiKeysHealthRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', `/payments/users/${user_pk}/api-keys/health/`);
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async usersApiKeysStatsRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', `/payments/users/${user_pk}/api-keys/stats/`);
  return response;
}

  /**
 * Get user API key summary. GET /api/users/{user_id}/api-keys/summary/
 */
async usersApiKeysSummaryRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
  const response = await this.client.request<Models.APIKeyDetail>('GET', `/payments/users/${user_pk}/api-keys/summary/`);
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersPaymentsList(user_pk: number, currency__code?: string | null, ordering?: string | null, page?: number | null, page_size?: number | null, provider?: string | null, search?: string | null, status?: string | null): Promise<Models.PaginatedPaymentListList[]> {
  const response = await this.client.request<Models.PaginatedPaymentListList[]>('GET', `/payments/users/${user_pk}/payments/`, { params: { currency__code, ordering, page, page_size, provider, search, status } });
  return (response as any).results || [];
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersPaymentsCreate(user_pk: number, data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
  const response = await this.client.request<Models.PaymentCreate>('POST', `/payments/users/${user_pk}/payments/`, { body: data });
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersPaymentsRetrieve(id: string, user_pk: number): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', `/payments/users/${user_pk}/payments/${id}/`);
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersPaymentsUpdate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('PUT', `/payments/users/${user_pk}/payments/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersPaymentsPartialUpdate(id: string, user_pk: number, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('PATCH', `/payments/users/${user_pk}/payments/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * Provides user-scoped access to payments with full CRUD operations.
 */
async usersPaymentsDestroy(id: string, user_pk: number): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/payments/users/${user_pk}/payments/${id}/`);
  return;
}

  /**
 * Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
 */
async usersPaymentsCancelCreate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('POST', `/payments/users/${user_pk}/payments/${id}/cancel/`, { body: data });
  return response;
}

  /**
 * Check payment status with provider. POST
 * /api/v1/users/{user_id}/payments/{id}/check_status/
 */
async usersPaymentsCheckStatusCreate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('POST', `/payments/users/${user_pk}/payments/${id}/check_status/`, { body: data });
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async usersPaymentsHealthRetrieve(user_pk: number): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', `/payments/users/${user_pk}/payments/health/`);
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async usersPaymentsStatsRetrieve(user_pk: number): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', `/payments/users/${user_pk}/payments/stats/`);
  return response;
}

  /**
 * Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
 */
async usersPaymentsSummaryRetrieve(user_pk: number): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', `/payments/users/${user_pk}/payments/summary/`);
  return response;
}

  /**
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * Provides user-scoped access to subscriptions with full CRUD operations.
 */
async usersSubscriptionsList(user_pk: number, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, status?: string | null, tier?: string | null): Promise<Models.PaginatedSubscriptionListList[]> {
  const response = await this.client.request<Models.PaginatedSubscriptionListList[]>('GET', `/payments/users/${user_pk}/subscriptions/`, { params: { ordering, page, page_size, search, status, tier } });
  return (response as any).results || [];
}

  /**
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * Provides user-scoped access to subscriptions with full CRUD operations.
 */
async usersSubscriptionsCreate(user_pk: number, data: Models.SubscriptionCreateRequest): Promise<Models.SubscriptionCreate> {
  const response = await this.client.request<Models.SubscriptionCreate>('POST', `/payments/users/${user_pk}/subscriptions/`, { body: data });
  return response;
}

  /**
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * Provides user-scoped access to subscriptions with full CRUD operations.
 */
async usersSubscriptionsRetrieve(id: string, user_pk: number): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', `/payments/users/${user_pk}/subscriptions/${id}/`);
  return response;
}

  /**
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * Provides user-scoped access to subscriptions with full CRUD operations.
 */
async usersSubscriptionsUpdate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('PUT', `/payments/users/${user_pk}/subscriptions/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * Provides user-scoped access to subscriptions with full CRUD operations.
 */
async usersSubscriptionsPartialUpdate(id: string, user_pk: number, data?: Models.PatchedSubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('PATCH', `/payments/users/${user_pk}/subscriptions/${id}/`, { body: data });
  return response;
}

  /**
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * Provides user-scoped access to subscriptions with full CRUD operations.
 */
async usersSubscriptionsDestroy(id: string, user_pk: number): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/payments/users/${user_pk}/subscriptions/${id}/`);
  return;
}

  /**
 * Increment subscription usage. POST
 * /api/users/{user_id}/subscriptions/{id}/increment_usage/
 */
async usersSubscriptionsIncrementUsageCreate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('POST', `/payments/users/${user_pk}/subscriptions/${id}/increment_usage/`, { body: data });
  return response;
}

  /**
 * Update subscription status. POST
 * /api/users/{user_id}/subscriptions/{id}/update_status/
 */
async usersSubscriptionsUpdateStatusCreate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('POST', `/payments/users/${user_pk}/subscriptions/${id}/update_status/`, { body: data });
  return response;
}

  /**
 * Get user's active subscription. GET
 * /api/users/{user_id}/subscriptions/active/
 */
async usersSubscriptionsActiveRetrieve(user_pk: number): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', `/payments/users/${user_pk}/subscriptions/active/`);
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async usersSubscriptionsHealthRetrieve(user_pk: number): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', `/payments/users/${user_pk}/subscriptions/health/`);
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async usersSubscriptionsStatsRetrieve(user_pk: number): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', `/payments/users/${user_pk}/subscriptions/stats/`);
  return response;
}

  /**
 * Get user subscription summary. GET
 * /api/users/{user_id}/subscriptions/summary/
 */
async usersSubscriptionsSummaryRetrieve(user_pk: number): Promise<Models.Subscription> {
  const response = await this.client.request<Models.Subscription>('GET', `/payments/users/${user_pk}/subscriptions/summary/`);
  return response;
}

  /**
 * Health check for the ViewSet and related services. Returns service
 * status and basic metrics.
 */
async usersHealthRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/users/health/");
  return response;
}

  /**
 * Get statistics for the current queryset. Returns counts, aggregates, and
 * breakdowns.
 */
async usersStatsRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/users/stats/");
  return response;
}

  /**
 * Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
 */
async usersSummaryRetrieve(): Promise<Models.Payment> {
  const response = await this.client.request<Models.Payment>('GET', "/payments/users/summary/");
  return response;
}

}