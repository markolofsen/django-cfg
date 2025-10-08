import * as Models from "./models";


/**
 * API endpoints for Payments.
 */
export class CfgPaymentsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async apiKeysList(is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string, user?: number): Promise<Models.PaginatedAPIKeyListList[]>;
  async apiKeysList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; user?: number }): Promise<Models.PaginatedAPIKeyListList[]>;

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async apiKeysList(...args: any[]): Promise<Models.PaginatedAPIKeyListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], ordering: args[1], page: args[2], page_size: args[3], search: args[4], user: args[5] };
    }
    const response = await this.client.request('GET', "/payments/api-keys/", { params });
    return (response as any).results || [];
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async apiKeysCreate(data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
    const response = await this.client.request('POST', "/payments/api-keys/", { body: data });
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async apiKeysRetrieve(id: string): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/payments/api-keys/${id}/`);
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async apiKeysUpdate(id: string, data: Models.APIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PUT', `/payments/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async apiKeysPartialUpdate(id: string, data?: Models.PatchedAPIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PATCH', `/payments/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async apiKeysDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/payments/api-keys/${id}/`);
    return;
  }

  /**
   * Perform action on API key. POST /api/api-keys/{id}/perform_action/
   */
  async apiKeysPerformActionCreate(id: string): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('POST', `/payments/api-keys/${id}/perform_action/`);
    return response;
  }

  /**
   * Get API key analytics. GET /api/api-keys/analytics/?days=30
   */
  async apiKeysAnalyticsRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/payments/api-keys/analytics/");
    return response;
  }

  /**
   * Get API keys grouped by user. GET /api/api-keys/by_user/
   */
  async apiKeysByUserRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/payments/api-keys/by_user/");
    return response;
  }

  /**
   * Standalone API key creation endpoint: /api/api-keys/create/ Simplified
   * endpoint for API key creation.
   */
  async apiKeysCreateCreate(data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
    const response = await this.client.request('POST', "/payments/api-keys/create/", { body: data });
    return response;
  }

  /**
   * Get API keys expiring soon. GET /api/api-keys/expiring_soon/?days=7
   */
  async apiKeysExpiringSoonRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/payments/api-keys/expiring_soon/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async apiKeysHealthRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/payments/api-keys/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async apiKeysStatsRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/payments/api-keys/stats/");
    return response;
  }

  /**
   * Validate API Key (Standalone)
   * 
   * Standalone endpoint to validate an API key and return key information
   */
  async apiKeysValidateCreate(data: Models.APIKeyValidationRequest): Promise<Models.APIKeyValidationResponse> {
    const response = await this.client.request('POST', "/payments/api-keys/validate/", { body: data });
    return response;
  }

  /**
   * Validate API Key
   * 
   * Validate an API key and return key information
   */
  async apiKeysValidateKeyCreate(data: Models.APIKeyValidationRequest): Promise<Models.APIKeyValidationResponse> {
    const response = await this.client.request('POST', "/payments/api-keys/validate_key/", { body: data });
    return response;
  }

  async balancesList(ordering?: string, page?: number, page_size?: number, search?: string, user?: number): Promise<Models.PaginatedUserBalanceList[]>;
  async balancesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; user?: number }): Promise<Models.PaginatedUserBalanceList[]>;

  /**
   * User balance ViewSet: /api/balances/ Read-only access to user balances
   * with statistics.
   */
  async balancesList(...args: any[]): Promise<Models.PaginatedUserBalanceList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3], user: args[4] };
    }
    const response = await this.client.request('GET', "/payments/balances/", { params });
    return (response as any).results || [];
  }

  /**
   * User balance ViewSet: /api/balances/ Read-only access to user balances
   * with statistics.
   */
  async balancesRetrieve(id: number): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', `/payments/balances/${id}/`);
    return response;
  }

  /**
   * Get balance analytics. GET /api/balances/analytics/?days=30
   */
  async balancesAnalyticsRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/payments/balances/analytics/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async balancesHealthRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/payments/balances/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async balancesStatsRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/payments/balances/stats/");
    return response;
  }

  /**
   * Get balance summary for all users. GET /api/balances/summary/
   */
  async balancesSummaryRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/payments/balances/summary/");
    return response;
  }

  async currenciesList(currency_type?: string, is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedCurrencyListList[]>;
  async currenciesList(params?: { currency_type?: string; is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedCurrencyListList[]>;

  /**
   * Currency ViewSet: /api/currencies/ Read-only access to currency
   * information with conversion capabilities.
   */
  async currenciesList(...args: any[]): Promise<Models.PaginatedCurrencyListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency_type: args[0], is_active: args[1], ordering: args[2], page: args[3], page_size: args[4], search: args[5] };
    }
    const response = await this.client.request('GET', "/payments/currencies/", { params });
    return (response as any).results || [];
  }

  /**
   * Disable create action.
   */
  async currenciesCreate(): Promise<Models.Currency> {
    const response = await this.client.request('POST', "/payments/currencies/");
    return response;
  }

  /**
   * Currency ViewSet: /api/currencies/ Read-only access to currency
   * information with conversion capabilities.
   */
  async currenciesRetrieve(id: number): Promise<Models.Currency> {
    const response = await this.client.request('GET', `/payments/currencies/${id}/`);
    return response;
  }

  /**
   * Get networks for specific currency. GET /api/currencies/{id}/networks/
   */
  async currenciesNetworksRetrieve(id: number): Promise<Models.Currency> {
    const response = await this.client.request('GET', `/payments/currencies/${id}/networks/`);
    return response;
  }

  /**
   * Get providers supporting specific currency. GET
   * /api/currencies/{id}/providers/
   */
  async currenciesProvidersRetrieve(id: number): Promise<Models.Currency> {
    const response = await this.client.request('GET', `/payments/currencies/${id}/providers/`);
    return response;
  }

  /**
   * Convert between currencies. POST /api/currencies/convert/
   */
  async currenciesConvertCreate(): Promise<Models.Currency> {
    const response = await this.client.request('POST', "/payments/currencies/convert/");
    return response;
  }

  /**
   * Get only cryptocurrencies. GET /api/currencies/crypto/
   */
  async currenciesCryptoRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/payments/currencies/crypto/");
    return response;
  }

  /**
   * Get only fiat currencies. GET /api/currencies/fiat/
   */
  async currenciesFiatRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/payments/currencies/fiat/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async currenciesHealthRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/payments/currencies/health/");
    return response;
  }

  async currenciesRatesRetrieve(base_currency: string, currencies: string): Promise<Models.Currency>;
  async currenciesRatesRetrieve(params?: { base_currency: string; currencies: string }): Promise<Models.Currency>;

  /**
   * Get exchange rates
   * 
   * Get current exchange rates for specified currencies
   */
  async currenciesRatesRetrieve(...args: any[]): Promise<Models.Currency> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { base_currency: args[0], currencies: args[1] };
    }
    const response = await this.client.request('GET', "/payments/currencies/rates/", { params });
    return response;
  }

  /**
   * Get only stablecoins. GET /api/currencies/stable/
   */
  async currenciesStableRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/payments/currencies/stable/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async currenciesStatsRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/payments/currencies/stats/");
    return response;
  }

  async currenciesSupportedRetrieve(currency_type?: string, provider?: string): Promise<Models.Currency>;
  async currenciesSupportedRetrieve(params?: { currency_type?: string; provider?: string }): Promise<Models.Currency>;

  /**
   * Get supported currencies
   * 
   * Get list of supported currencies from payment providers
   */
  async currenciesSupportedRetrieve(...args: any[]): Promise<Models.Currency> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency_type: args[0], provider: args[1] };
    }
    const response = await this.client.request('GET', "/payments/currencies/supported/", { params });
    return response;
  }

  async endpointGroupsList(is_enabled?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedEndpointGroupList[]>;
  async endpointGroupsList(params?: { is_enabled?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedEndpointGroupList[]>;

  /**
   * Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
   * endpoint group information.
   */
  async endpointGroupsList(...args: any[]): Promise<Models.PaginatedEndpointGroupList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_enabled: args[0], ordering: args[1], page: args[2], page_size: args[3], search: args[4] };
    }
    const response = await this.client.request('GET', "/payments/endpoint-groups/", { params });
    return (response as any).results || [];
  }

  /**
   * Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
   * endpoint group information.
   */
  async endpointGroupsRetrieve(id: number): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', `/payments/endpoint-groups/${id}/`);
    return response;
  }

  /**
   * Get available endpoint groups for subscription. GET
   * /api/endpoint-groups/available/
   */
  async endpointGroupsAvailableRetrieve(): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', "/payments/endpoint-groups/available/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async endpointGroupsHealthRetrieve(): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', "/payments/endpoint-groups/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async endpointGroupsStatsRetrieve(): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', "/payments/endpoint-groups/stats/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async healthRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/health/");
    return response;
  }

  async networksList(is_active?: boolean, native_currency__code?: string, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedNetworkList[]>;
  async networksList(params?: { is_active?: boolean; native_currency__code?: string; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedNetworkList[]>;

  /**
   * Network ViewSet: /api/networks/ Read-only access to blockchain network
   * information.
   */
  async networksList(...args: any[]): Promise<Models.PaginatedNetworkList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], native_currency__code: args[1], ordering: args[2], page: args[3], page_size: args[4], search: args[5] };
    }
    const response = await this.client.request('GET', "/payments/networks/", { params });
    return (response as any).results || [];
  }

  /**
   * Network ViewSet: /api/networks/ Read-only access to blockchain network
   * information.
   */
  async networksRetrieve(id: number): Promise<Models.Network> {
    const response = await this.client.request('GET', `/payments/networks/${id}/`);
    return response;
  }

  /**
   * Get networks grouped by currency. GET /api/networks/by_currency/
   */
  async networksByCurrencyRetrieve(): Promise<Models.Network> {
    const response = await this.client.request('GET', "/payments/networks/by_currency/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async networksHealthRetrieve(): Promise<Models.Network> {
    const response = await this.client.request('GET', "/payments/networks/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async networksStatsRetrieve(): Promise<Models.Network> {
    const response = await this.client.request('GET', "/payments/networks/stats/");
    return response;
  }

  /**
   * API Keys Overview
   * 
   * Get API keys overview
   */
  async overviewDashboardApiKeysOverviewRetrieve(): Promise<Models.APIKeysOverview> {
    const response = await this.client.request('GET', "/payments/overview/dashboard/api_keys_overview/");
    return response;
  }

  /**
   * Balance Overview
   * 
   * Get user balance overview
   */
  async overviewDashboardBalanceOverviewRetrieve(): Promise<Models.BalanceOverview> {
    const response = await this.client.request('GET', "/payments/overview/dashboard/balance_overview/");
    return response;
  }

  async overviewDashboardChartDataRetrieve(period?: string): Promise<Models.PaymentsChartResponse>;
  async overviewDashboardChartDataRetrieve(params?: { period?: string }): Promise<Models.PaymentsChartResponse>;

  /**
   * Payments Chart Data
   * 
   * Get chart data for payments visualization
   */
  async overviewDashboardChartDataRetrieve(...args: any[]): Promise<Models.PaymentsChartResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { period: args[0] };
    }
    const response = await this.client.request('GET', "/payments/overview/dashboard/chart_data/", { params });
    return response;
  }

  /**
   * Payments Dashboard Metrics
   * 
   * Get payments dashboard metrics including balance, subscriptions, API
   * keys, and payments
   */
  async overviewDashboardMetricsRetrieve(): Promise<Models.PaymentsMetrics> {
    const response = await this.client.request('GET', "/payments/overview/dashboard/metrics/");
    return response;
  }

  /**
   * Payments Dashboard Overview
   * 
   * Get complete payments dashboard overview with metrics, recent payments,
   * and analytics
   */
  async overviewDashboardOverviewRetrieve(): Promise<Models.PaymentsDashboardOverview> {
    const response = await this.client.request('GET', "/payments/overview/dashboard/overview/");
    return response;
  }

  async overviewDashboardPaymentAnalyticsRetrieve(limit?: number): Promise<Models.PaymentAnalyticsResponse>;
  async overviewDashboardPaymentAnalyticsRetrieve(params?: { limit?: number }): Promise<Models.PaymentAnalyticsResponse>;

  /**
   * Payment Analytics
   * 
   * Get analytics for payments by currency and provider
   */
  async overviewDashboardPaymentAnalyticsRetrieve(...args: any[]): Promise<Models.PaymentAnalyticsResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0] };
    }
    const response = await this.client.request('GET', "/payments/overview/dashboard/payment_analytics/", { params });
    return response;
  }

  async overviewDashboardRecentPaymentsList(limit?: number, page?: number, page_size?: number): Promise<Models.PaginatedRecentPaymentList[]>;
  async overviewDashboardRecentPaymentsList(params?: { limit?: number; page?: number; page_size?: number }): Promise<Models.PaginatedRecentPaymentList[]>;

  /**
   * Recent Payments
   * 
   * Get recent payments for the user
   */
  async overviewDashboardRecentPaymentsList(...args: any[]): Promise<Models.PaginatedRecentPaymentList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0], page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', "/payments/overview/dashboard/recent_payments/", { params });
    return (response as any).results || [];
  }

  async overviewDashboardRecentTransactionsList(limit?: number, page?: number, page_size?: number): Promise<Models.PaginatedRecentTransactionList[]>;
  async overviewDashboardRecentTransactionsList(params?: { limit?: number; page?: number; page_size?: number }): Promise<Models.PaginatedRecentTransactionList[]>;

  /**
   * Recent Transactions
   * 
   * Get recent balance transactions for the user
   */
  async overviewDashboardRecentTransactionsList(...args: any[]): Promise<Models.PaginatedRecentTransactionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0], page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', "/payments/overview/dashboard/recent_transactions/", { params });
    return (response as any).results || [];
  }

  /**
   * Subscription Overview
   * 
   * Get current subscription overview
   */
  async overviewDashboardSubscriptionOverviewRetrieve(): Promise<Models.SubscriptionOverview> {
    const response = await this.client.request('GET', "/payments/overview/dashboard/subscription_overview/");
    return response;
  }

  async paymentsList(currency__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string, status?: string, user?: number): Promise<Models.PaginatedPaymentListList[]>;
  async paymentsList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number }): Promise<Models.PaginatedPaymentListList[]>;

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async paymentsList(...args: any[]): Promise<Models.PaginatedPaymentListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency__code: args[0], ordering: args[1], page: args[2], page_size: args[3], provider: args[4], search: args[5], status: args[6], user: args[7] };
    }
    const response = await this.client.request('GET', "/payments/payments/", { params });
    return (response as any).results || [];
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async paymentsCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', "/payments/payments/", { body: data });
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async paymentsRetrieve(id: string): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/payments/payments/${id}/`);
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async paymentsUpdate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PUT', `/payments/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async paymentsPartialUpdate(id: string, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PATCH', `/payments/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async paymentsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/payments/payments/${id}/`);
    return;
  }

  /**
   * Cancel payment. POST /api/v1/payments/{id}/cancel/
   */
  async paymentsCancelCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/payments/payments/${id}/cancel/`, { body: data });
    return response;
  }

  /**
   * Check payment status with provider. POST
   * /api/v1/payments/{id}/check_status/
   */
  async paymentsCheckStatusCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/payments/payments/${id}/check_status/`, { body: data });
    return response;
  }

  /**
   * Get payment analytics. GET /api/v1/payments/analytics/?days=30
   */
  async paymentsAnalyticsRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/payments/analytics/");
    return response;
  }

  /**
   * Get payments grouped by provider. GET /api/v1/payments/by_provider/
   */
  async paymentsByProviderRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/payments/by_provider/");
    return response;
  }

  /**
   * Standalone payment creation endpoint: /api/v1/payments/create/
   * Simplified endpoint for payment creation without full ViewSet overhead.
   */
  async paymentsCreateCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', "/payments/payments/create/", { body: data });
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async paymentsHealthRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/payments/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async paymentsStatsRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/payments/stats/");
    return response;
  }

  /**
   * Standalone payment status endpoint: /api/v1/payments/{id}/status/ Quick
   * status check without full ViewSet overhead.
   */
  async paymentsStatusRetrieve(id: string): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/payments/payments/status/${id}/`);
    return response;
  }

  async providerCurrenciesList(currency__code?: string, is_enabled?: boolean, network__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string): Promise<Models.PaginatedProviderCurrencyList[]>;
  async providerCurrenciesList(params?: { currency__code?: string; is_enabled?: boolean; network__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string }): Promise<Models.PaginatedProviderCurrencyList[]>;

  /**
   * Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
   * provider-specific currency information.
   */
  async providerCurrenciesList(...args: any[]): Promise<Models.PaginatedProviderCurrencyList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency__code: args[0], is_enabled: args[1], network__code: args[2], ordering: args[3], page: args[4], page_size: args[5], provider: args[6], search: args[7] };
    }
    const response = await this.client.request('GET', "/payments/provider-currencies/", { params });
    return (response as any).results || [];
  }

  /**
   * Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
   * provider-specific currency information.
   */
  async providerCurrenciesRetrieve(id: number): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', `/payments/provider-currencies/${id}/`);
    return response;
  }

  /**
   * Get provider currencies grouped by provider. GET
   * /api/provider-currencies/by_provider/
   */
  async providerCurrenciesByProviderRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/payments/provider-currencies/by_provider/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async providerCurrenciesHealthRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/payments/provider-currencies/health/");
    return response;
  }

  /**
   * Get currency limits by provider. GET
   * /api/provider-currencies/limits/?provider=nowpayments
   */
  async providerCurrenciesLimitsRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/payments/provider-currencies/limits/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async providerCurrenciesStatsRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/payments/provider-currencies/stats/");
    return response;
  }

  async subscriptionsList(ordering?: string, page?: number, page_size?: number, search?: string, status?: string, tier?: string, user?: number): Promise<Models.PaginatedSubscriptionListList[]>;
  async subscriptionsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string; user?: number }): Promise<Models.PaginatedSubscriptionListList[]>;

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async subscriptionsList(...args: any[]): Promise<Models.PaginatedSubscriptionListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3], status: args[4], tier: args[5], user: args[6] };
    }
    const response = await this.client.request('GET', "/payments/subscriptions/", { params });
    return (response as any).results || [];
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async subscriptionsCreate(data: Models.SubscriptionCreateRequest): Promise<Models.SubscriptionCreate> {
    const response = await this.client.request('POST', "/payments/subscriptions/", { body: data });
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async subscriptionsRetrieve(id: string): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/payments/subscriptions/${id}/`);
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async subscriptionsUpdate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PUT', `/payments/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async subscriptionsPartialUpdate(id: string, data?: Models.PatchedSubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PATCH', `/payments/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async subscriptionsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/payments/subscriptions/${id}/`);
    return;
  }

  /**
   * Increment subscription usage. POST
   * /api/subscriptions/{id}/increment_usage/
   */
  async subscriptionsIncrementUsageCreate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/payments/subscriptions/${id}/increment_usage/`, { body: data });
    return response;
  }

  /**
   * Update subscription status. POST /api/subscriptions/{id}/update_status/
   */
  async subscriptionsUpdateStatusCreate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/payments/subscriptions/${id}/update_status/`, { body: data });
    return response;
  }

  /**
   * Get subscription analytics. GET /api/subscriptions/analytics/?days=30
   */
  async subscriptionsAnalyticsRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/payments/subscriptions/analytics/");
    return response;
  }

  /**
   * Get subscriptions grouped by status. GET /api/subscriptions/by_status/
   */
  async subscriptionsByStatusRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/payments/subscriptions/by_status/");
    return response;
  }

  /**
   * Get subscriptions grouped by tier. GET /api/subscriptions/by_tier/
   */
  async subscriptionsByTierRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/payments/subscriptions/by_tier/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async subscriptionsHealthRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/payments/subscriptions/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async subscriptionsStatsRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/payments/subscriptions/stats/");
    return response;
  }

  async tariffsList(is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedTariffList[]>;
  async tariffsList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedTariffList[]>;

  /**
   * Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
   * subscription selection.
   */
  async tariffsList(...args: any[]): Promise<Models.PaginatedTariffList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], ordering: args[1], page: args[2], page_size: args[3], search: args[4] };
    }
    const response = await this.client.request('GET', "/payments/tariffs/", { params });
    return (response as any).results || [];
  }

  /**
   * Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
   * subscription selection.
   */
  async tariffsRetrieve(id: number): Promise<Models.Tariff> {
    const response = await this.client.request('GET', `/payments/tariffs/${id}/`);
    return response;
  }

  /**
   * Get endpoint groups for specific tariff. GET
   * /api/tariffs/{id}/endpoint_groups/
   */
  async tariffsEndpointGroupsRetrieve(id: number): Promise<Models.Tariff> {
    const response = await this.client.request('GET', `/payments/tariffs/${id}/endpoint_groups/`);
    return response;
  }

  /**
   * Get free tariffs. GET /api/tariffs/free/
   */
  async tariffsFreeRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/payments/tariffs/free/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async tariffsHealthRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/payments/tariffs/health/");
    return response;
  }

  /**
   * Get paid tariffs. GET /api/tariffs/paid/
   */
  async tariffsPaidRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/payments/tariffs/paid/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async tariffsStatsRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/payments/tariffs/stats/");
    return response;
  }

  async transactionsList(ordering?: string, page?: number, page_size?: number, payment_id?: string, search?: string, transaction_type?: string, user?: number): Promise<Models.PaginatedTransactionList[]>;
  async transactionsList(params?: { ordering?: string; page?: number; page_size?: number; payment_id?: string; search?: string; transaction_type?: string; user?: number }): Promise<Models.PaginatedTransactionList[]>;

  /**
   * Transaction ViewSet: /api/transactions/ Read-only access to transaction
   * history with filtering.
   */
  async transactionsList(...args: any[]): Promise<Models.PaginatedTransactionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], payment_id: args[3], search: args[4], transaction_type: args[5], user: args[6] };
    }
    const response = await this.client.request('GET', "/payments/transactions/", { params });
    return (response as any).results || [];
  }

  /**
   * Transaction ViewSet: /api/transactions/ Read-only access to transaction
   * history with filtering.
   */
  async transactionsRetrieve(id: string): Promise<Models.Transaction> {
    const response = await this.client.request('GET', `/payments/transactions/${id}/`);
    return response;
  }

  /**
   * Get transactions grouped by type. GET /api/transactions/by_type/
   */
  async transactionsByTypeRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/payments/transactions/by_type/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async transactionsHealthRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/payments/transactions/health/");
    return response;
  }

  /**
   * Get recent transactions. GET /api/transactions/recent/?limit=10
   */
  async transactionsRecentRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/payments/transactions/recent/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async transactionsStatsRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/payments/transactions/stats/");
    return response;
  }

  async usersList(currency__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string, status?: string): Promise<Models.PaginatedPaymentListList[]>;
  async usersList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }): Promise<Models.PaginatedPaymentListList[]>;

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersList(...args: any[]): Promise<Models.PaginatedPaymentListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency__code: args[0], ordering: args[1], page: args[2], page_size: args[3], provider: args[4], search: args[5], status: args[6] };
    }
    const response = await this.client.request('GET', "/payments/users/", { params });
    return (response as any).results || [];
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', "/payments/users/", { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersRetrieve(id: string): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/payments/users/${id}/`);
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersUpdate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PUT', `/payments/users/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersPartialUpdate(id: string, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PATCH', `/payments/users/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/payments/users/${id}/`);
    return;
  }

  /**
   * Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
   */
  async usersCancelCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/payments/users/${id}/cancel/`, { body: data });
    return response;
  }

  /**
   * Check payment status with provider. POST
   * /api/v1/users/{user_id}/payments/{id}/check_status/
   */
  async usersCheckStatusCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/payments/users/${id}/check_status/`, { body: data });
    return response;
  }

  async usersApiKeysList(user_pk: number, is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedAPIKeyListList[]>;
  async usersApiKeysList(user_pk: number, params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedAPIKeyListList[]>;

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async usersApiKeysList(...args: any[]): Promise<Models.PaginatedAPIKeyListList[]> {
    const user_pk = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { is_active: args[1], ordering: args[2], page: args[3], page_size: args[4], search: args[5] };
    }
    const response = await this.client.request('GET', `/payments/users/${user_pk}/api-keys/`, { params });
    return (response as any).results || [];
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async usersApiKeysCreate(user_pk: number, data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/api-keys/`, { body: data });
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async usersApiKeysRetrieve(id: string, user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/api-keys/${id}/`);
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async usersApiKeysUpdate(id: string, user_pk: number, data: Models.APIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PUT', `/payments/users/${user_pk}/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async usersApiKeysPartialUpdate(id: string, user_pk: number, data?: Models.PatchedAPIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PATCH', `/payments/users/${user_pk}/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async usersApiKeysDestroy(id: string, user_pk: number): Promise<void> {
    const response = await this.client.request('DELETE', `/payments/users/${user_pk}/api-keys/${id}/`);
    return;
  }

  /**
   * Perform action on API key. POST
   * /api/users/{user_id}/api-keys/{id}/perform_action/
   */
  async usersApiKeysPerformActionCreate(id: string, user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/api-keys/${id}/perform_action/`);
    return response;
  }

  /**
   * Get user's active API keys. GET /api/users/{user_id}/api-keys/active/
   */
  async usersApiKeysActiveRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/api-keys/active/`);
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async usersApiKeysHealthRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/api-keys/health/`);
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async usersApiKeysStatsRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/api-keys/stats/`);
    return response;
  }

  /**
   * Get user API key summary. GET /api/users/{user_id}/api-keys/summary/
   */
  async usersApiKeysSummaryRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/api-keys/summary/`);
    return response;
  }

  async usersPaymentsList(user_pk: number, currency__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string, status?: string): Promise<Models.PaginatedPaymentListList[]>;
  async usersPaymentsList(user_pk: number, params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }): Promise<Models.PaginatedPaymentListList[]>;

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersPaymentsList(...args: any[]): Promise<Models.PaginatedPaymentListList[]> {
    const user_pk = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { currency__code: args[1], ordering: args[2], page: args[3], page_size: args[4], provider: args[5], search: args[6], status: args[7] };
    }
    const response = await this.client.request('GET', `/payments/users/${user_pk}/payments/`, { params });
    return (response as any).results || [];
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersPaymentsCreate(user_pk: number, data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/payments/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersPaymentsRetrieve(id: string, user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/payments/${id}/`);
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersPaymentsUpdate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PUT', `/payments/users/${user_pk}/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersPaymentsPartialUpdate(id: string, user_pk: number, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PATCH', `/payments/users/${user_pk}/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async usersPaymentsDestroy(id: string, user_pk: number): Promise<void> {
    const response = await this.client.request('DELETE', `/payments/users/${user_pk}/payments/${id}/`);
    return;
  }

  /**
   * Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
   */
  async usersPaymentsCancelCreate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/payments/${id}/cancel/`, { body: data });
    return response;
  }

  /**
   * Check payment status with provider. POST
   * /api/v1/users/{user_id}/payments/{id}/check_status/
   */
  async usersPaymentsCheckStatusCreate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/payments/${id}/check_status/`, { body: data });
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async usersPaymentsHealthRetrieve(user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/payments/health/`);
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async usersPaymentsStatsRetrieve(user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/payments/stats/`);
    return response;
  }

  /**
   * Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
   */
  async usersPaymentsSummaryRetrieve(user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/payments/summary/`);
    return response;
  }

  async usersSubscriptionsList(user_pk: number, ordering?: string, page?: number, page_size?: number, search?: string, status?: string, tier?: string): Promise<Models.PaginatedSubscriptionListList[]>;
  async usersSubscriptionsList(user_pk: number, params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string }): Promise<Models.PaginatedSubscriptionListList[]>;

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async usersSubscriptionsList(...args: any[]): Promise<Models.PaginatedSubscriptionListList[]> {
    const user_pk = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { ordering: args[1], page: args[2], page_size: args[3], search: args[4], status: args[5], tier: args[6] };
    }
    const response = await this.client.request('GET', `/payments/users/${user_pk}/subscriptions/`, { params });
    return (response as any).results || [];
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async usersSubscriptionsCreate(user_pk: number, data: Models.SubscriptionCreateRequest): Promise<Models.SubscriptionCreate> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/subscriptions/`, { body: data });
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async usersSubscriptionsRetrieve(id: string, user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/subscriptions/${id}/`);
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async usersSubscriptionsUpdate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PUT', `/payments/users/${user_pk}/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async usersSubscriptionsPartialUpdate(id: string, user_pk: number, data?: Models.PatchedSubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PATCH', `/payments/users/${user_pk}/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async usersSubscriptionsDestroy(id: string, user_pk: number): Promise<void> {
    const response = await this.client.request('DELETE', `/payments/users/${user_pk}/subscriptions/${id}/`);
    return;
  }

  /**
   * Increment subscription usage. POST
   * /api/users/{user_id}/subscriptions/{id}/increment_usage/
   */
  async usersSubscriptionsIncrementUsageCreate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/subscriptions/${id}/increment_usage/`, { body: data });
    return response;
  }

  /**
   * Update subscription status. POST
   * /api/users/{user_id}/subscriptions/{id}/update_status/
   */
  async usersSubscriptionsUpdateStatusCreate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/payments/users/${user_pk}/subscriptions/${id}/update_status/`, { body: data });
    return response;
  }

  /**
   * Get user's active subscription. GET
   * /api/users/{user_id}/subscriptions/active/
   */
  async usersSubscriptionsActiveRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/subscriptions/active/`);
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async usersSubscriptionsHealthRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/subscriptions/health/`);
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async usersSubscriptionsStatsRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/subscriptions/stats/`);
    return response;
  }

  /**
   * Get user subscription summary. GET
   * /api/users/{user_id}/subscriptions/summary/
   */
  async usersSubscriptionsSummaryRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/payments/users/${user_pk}/subscriptions/summary/`);
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async usersHealthRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/users/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async usersStatsRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/users/stats/");
    return response;
  }

  /**
   * Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
   */
  async usersSummaryRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/payments/users/summary/");
    return response;
  }

}