import * as Models from "./models";


/**
 * API endpoints for Cfg Payments.
 */
export class CfgPaymentsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async cfgPaymentsAdminApiPaymentsList(currency__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string, status?: string, user?: number): Promise<Models.PaginatedAdminPaymentListList[]>;
  async cfgPaymentsAdminApiPaymentsList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number }): Promise<Models.PaginatedAdminPaymentListList[]>;

  /**
   * Admin ViewSet for payment management. Provides full CRUD operations for
   * payments with admin-specific features.
   */
  async cfgPaymentsAdminApiPaymentsList(...args: any[]): Promise<Models.PaginatedAdminPaymentListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency__code: args[0], ordering: args[1], page: args[2], page_size: args[3], provider: args[4], search: args[5], status: args[6], user: args[7] };
    }
    const response = await this.client.request('GET', "/cfg/payments/admin/api/payments/", { params });
    return (response as any).results || [];
  }

  /**
   * Create payment with enhanced error handling.
   */
  async cfgPaymentsAdminApiPaymentsCreate(data: Models.AdminPaymentCreateRequest): Promise<Models.AdminPaymentCreate> {
    const response = await this.client.request('POST', "/cfg/payments/admin/api/payments/", { body: data });
    return response;
  }

  /**
   * Admin ViewSet for payment management. Provides full CRUD operations for
   * payments with admin-specific features.
   */
  async cfgPaymentsAdminApiPaymentsRetrieve(id: string): Promise<Models.AdminPaymentDetail> {
    const response = await this.client.request('GET', `/cfg/payments/admin/api/payments/${id}/`);
    return response;
  }

  /**
   * Admin ViewSet for payment management. Provides full CRUD operations for
   * payments with admin-specific features.
   */
  async cfgPaymentsAdminApiPaymentsUpdate(id: string, data: Models.AdminPaymentUpdateRequest): Promise<Models.AdminPaymentUpdate> {
    const response = await this.client.request('PUT', `/cfg/payments/admin/api/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * Admin ViewSet for payment management. Provides full CRUD operations for
   * payments with admin-specific features.
   */
  async cfgPaymentsAdminApiPaymentsPartialUpdate(id: string, data?: Models.PatchedAdminPaymentUpdateRequest): Promise<Models.AdminPaymentUpdate> {
    const response = await this.client.request('PATCH', `/cfg/payments/admin/api/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * Admin ViewSet for payment management. Provides full CRUD operations for
   * payments with admin-specific features.
   */
  async cfgPaymentsAdminApiPaymentsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/admin/api/payments/${id}/`);
    return;
  }

  /**
   * Cancel a payment.
   */
  async cfgPaymentsAdminApiPaymentsCancelCreate(id: string): Promise<Models.AdminPaymentDetail> {
    const response = await this.client.request('POST', `/cfg/payments/admin/api/payments/${id}/cancel/`);
    return response;
  }

  /**
   * Refresh payment status from provider via AJAX.
   */
  async cfgPaymentsAdminApiPaymentsRefreshStatusCreate(id: string): Promise<Models.AdminPaymentDetail> {
    const response = await this.client.request('POST', `/cfg/payments/admin/api/payments/${id}/refresh_status/`);
    return response;
  }

  /**
   * Refund a payment.
   */
  async cfgPaymentsAdminApiPaymentsRefundCreate(id: string): Promise<Models.AdminPaymentDetail> {
    const response = await this.client.request('POST', `/cfg/payments/admin/api/payments/${id}/refund/`);
    return response;
  }

  /**
   * Get comprehensive payment statistics.
   */
  async cfgPaymentsAdminApiPaymentsStatsRetrieve(): Promise<Models.AdminPaymentStats> {
    const response = await this.client.request('GET', "/cfg/payments/admin/api/payments/stats/");
    return response;
  }

  async cfgPaymentsAdminApiStatsList(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedAdminPaymentStatsList[]>;
  async cfgPaymentsAdminApiStatsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedAdminPaymentStatsList[]>;

  /**
   * Get overview statistics.
   */
  async cfgPaymentsAdminApiStatsList(...args: any[]): Promise<Models.PaginatedAdminPaymentStatsList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/cfg/payments/admin/api/stats/", { params });
    return (response as any).results || [];
  }

  /**
   * Admin ViewSet for comprehensive system statistics. Provides aggregated
   * statistics across all system components.
   */
  async cfgPaymentsAdminApiStatsRetrieve(id: string): Promise<Models.AdminPaymentStats> {
    const response = await this.client.request('GET', `/cfg/payments/admin/api/stats/${id}/`);
    return response;
  }

  /**
   * Get detailed payment statistics.
   */
  async cfgPaymentsAdminApiStatsPaymentsRetrieve(): Promise<Models.AdminPaymentStats> {
    const response = await this.client.request('GET', "/cfg/payments/admin/api/stats/payments/");
    return response;
  }

  /**
   * Get system health and performance statistics.
   */
  async cfgPaymentsAdminApiStatsSystemRetrieve(): Promise<Models.AdminPaymentStats> {
    const response = await this.client.request('GET', "/cfg/payments/admin/api/stats/system/");
    return response;
  }

  /**
   * Get detailed webhook statistics.
   */
  async cfgPaymentsAdminApiStatsWebhooksRetrieve(): Promise<Models.AdminPaymentStats> {
    const response = await this.client.request('GET', "/cfg/payments/admin/api/stats/webhooks/");
    return response;
  }

  async cfgPaymentsAdminApiUsersList(is_active?: boolean, is_staff?: boolean, is_superuser?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedAdminUserList[]>;
  async cfgPaymentsAdminApiUsersList(params?: { is_active?: boolean; is_staff?: boolean; is_superuser?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedAdminUserList[]>;

  /**
   * Override list to limit results for dropdown.
   */
  async cfgPaymentsAdminApiUsersList(...args: any[]): Promise<Models.PaginatedAdminUserList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], is_staff: args[1], is_superuser: args[2], ordering: args[3], page: args[4], page_size: args[5], search: args[6] };
    }
    const response = await this.client.request('GET', "/cfg/payments/admin/api/users/", { params });
    return (response as any).results || [];
  }

  /**
   * Admin ViewSet for user management. Provides read-only access to users
   * for admin interface.
   */
  async cfgPaymentsAdminApiUsersRetrieve(id: number): Promise<Models.AdminUser> {
    const response = await this.client.request('GET', `/cfg/payments/admin/api/users/${id}/`);
    return response;
  }

  /**
   * Test webhook endpoint. Sends a test webhook to the specified URL with
   * the given event type. Useful for developers to test their webhook
   * implementations.
   */
  async cfgPaymentsAdminApiWebhookTestTestCreate(data: Models.WebhookStatsRequest): Promise<Models.WebhookStats> {
    const response = await this.client.request('POST', "/cfg/payments/admin/api/webhook-test/test/", { body: data });
    return response;
  }

  async cfgPaymentsAdminApiWebhooksList(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedWebhookStatsList[]>;
  async cfgPaymentsAdminApiWebhooksList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedWebhookStatsList[]>;

  /**
   * List webhook providers and configurations with real ngrok URLs.
   */
  async cfgPaymentsAdminApiWebhooksList(...args: any[]): Promise<Models.PaginatedWebhookStatsList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/cfg/payments/admin/api/webhooks/", { params });
    return (response as any).results || [];
  }

  /**
   * Admin ViewSet for webhook configuration management. Read-only view for
   * webhook configurations and provider info. Requires admin permissions.
   */
  async cfgPaymentsAdminApiWebhooksRetrieve(id: string): Promise<Models.WebhookStats> {
    const response = await this.client.request('GET', `/cfg/payments/admin/api/webhooks/${id}/`);
    return response;
  }

  async cfgPaymentsAdminApiWebhooksEventsList(webhook_pk: string, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedWebhookEventListList[]>;
  async cfgPaymentsAdminApiWebhooksEventsList(webhook_pk: string, params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedWebhookEventListList[]>;

  /**
   * List webhook events with filtering and pagination.
   */
  async cfgPaymentsAdminApiWebhooksEventsList(...args: any[]): Promise<Models.PaginatedWebhookEventListList[]> {
    const webhook_pk = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { ordering: args[1], page: args[2], page_size: args[3], search: args[4] };
    }
    const response = await this.client.request('GET', `/cfg/payments/admin/api/webhooks/${webhook_pk}/events/`, { params });
    return (response as any).results || [];
  }

  /**
   * Admin ViewSet for webhook events management. Provides listing,
   * filtering, and actions for webhook events. Requires admin permissions.
   */
  async cfgPaymentsAdminApiWebhooksEventsRetrieve(id: string, webhook_pk: string): Promise<Models.WebhookEventList[]> {
    const response = await this.client.request('GET', `/cfg/payments/admin/api/webhooks/${webhook_pk}/events/${id}/`);
    return (response as any).results || [];
  }

  /**
   * Retry a failed webhook event.
   */
  async cfgPaymentsAdminApiWebhooksEventsRetryCreate(id: string, webhook_pk: string, data: Models.WebhookEventListRequest): Promise<Models.WebhookEventList> {
    const response = await this.client.request('POST', `/cfg/payments/admin/api/webhooks/${webhook_pk}/events/${id}/retry/`, { body: data });
    return response;
  }

  /**
   * Clear all webhook events.
   */
  async cfgPaymentsAdminApiWebhooksEventsClearAllCreate(webhook_pk: string, data: Models.WebhookEventListRequest): Promise<Models.WebhookEventList> {
    const response = await this.client.request('POST', `/cfg/payments/admin/api/webhooks/${webhook_pk}/events/clear_all/`, { body: data });
    return response;
  }

  /**
   * Retry all failed webhook events.
   */
  async cfgPaymentsAdminApiWebhooksEventsRetryFailedCreate(webhook_pk: string, data: Models.WebhookEventListRequest): Promise<Models.WebhookEventList> {
    const response = await this.client.request('POST', `/cfg/payments/admin/api/webhooks/${webhook_pk}/events/retry_failed/`, { body: data });
    return response;
  }

  /**
   * Get webhook statistics.
   */
  async cfgPaymentsAdminApiWebhooksStatsRetrieve(): Promise<Models.WebhookStats> {
    const response = await this.client.request('GET', "/cfg/payments/admin/api/webhooks/stats/");
    return response;
  }

  async cfgPaymentsApiKeysList(is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string, user?: number): Promise<Models.PaginatedAPIKeyListList[]>;
  async cfgPaymentsApiKeysList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; user?: number }): Promise<Models.PaginatedAPIKeyListList[]>;

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async cfgPaymentsApiKeysList(...args: any[]): Promise<Models.PaginatedAPIKeyListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], ordering: args[1], page: args[2], page_size: args[3], search: args[4], user: args[5] };
    }
    const response = await this.client.request('GET', "/cfg/payments/api-keys/", { params });
    return (response as any).results || [];
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async cfgPaymentsApiKeysCreate(data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
    const response = await this.client.request('POST', "/cfg/payments/api-keys/", { body: data });
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async cfgPaymentsApiKeysRetrieve(id: string): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/cfg/payments/api-keys/${id}/`);
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async cfgPaymentsApiKeysUpdate(id: string, data: Models.APIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PUT', `/cfg/payments/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async cfgPaymentsApiKeysPartialUpdate(id: string, data?: Models.PatchedAPIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PATCH', `/cfg/payments/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * Global API Key ViewSet: /api/api-keys/ Provides admin-level access to
   * all API keys with filtering and stats.
   */
  async cfgPaymentsApiKeysDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/api-keys/${id}/`);
    return;
  }

  /**
   * Perform action on API key. POST /api/api-keys/{id}/perform_action/
   */
  async cfgPaymentsApiKeysPerformActionCreate(id: string): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('POST', `/cfg/payments/api-keys/${id}/perform_action/`);
    return response;
  }

  /**
   * Get API key analytics. GET /api/api-keys/analytics/?days=30
   */
  async cfgPaymentsApiKeysAnalyticsRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/cfg/payments/api-keys/analytics/");
    return response;
  }

  /**
   * Get API keys grouped by user. GET /api/api-keys/by_user/
   */
  async cfgPaymentsApiKeysByUserRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/cfg/payments/api-keys/by_user/");
    return response;
  }

  /**
   * Standalone API key creation endpoint: /api/api-keys/create/ Simplified
   * endpoint for API key creation.
   */
  async cfgPaymentsApiKeysCreateCreate(data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
    const response = await this.client.request('POST', "/cfg/payments/api-keys/create/", { body: data });
    return response;
  }

  /**
   * Get API keys expiring soon. GET /api/api-keys/expiring_soon/?days=7
   */
  async cfgPaymentsApiKeysExpiringSoonRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/cfg/payments/api-keys/expiring_soon/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsApiKeysHealthRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/cfg/payments/api-keys/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsApiKeysStatsRetrieve(): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', "/cfg/payments/api-keys/stats/");
    return response;
  }

  /**
   * Validate API Key (Standalone)
   * 
   * Standalone endpoint to validate an API key and return key information
   */
  async cfgPaymentsApiKeysValidateCreate(data: Models.APIKeyValidationRequest): Promise<Models.APIKeyValidationResponse> {
    const response = await this.client.request('POST', "/cfg/payments/api-keys/validate/", { body: data });
    return response;
  }

  /**
   * Validate API Key
   * 
   * Validate an API key and return key information
   */
  async cfgPaymentsApiKeysValidateKeyCreate(data: Models.APIKeyValidationRequest): Promise<Models.APIKeyValidationResponse> {
    const response = await this.client.request('POST', "/cfg/payments/api-keys/validate_key/", { body: data });
    return response;
  }

  async cfgPaymentsBalancesList(ordering?: string, page?: number, page_size?: number, search?: string, user?: number): Promise<Models.PaginatedUserBalanceList[]>;
  async cfgPaymentsBalancesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; user?: number }): Promise<Models.PaginatedUserBalanceList[]>;

  /**
   * User balance ViewSet: /api/balances/ Read-only access to user balances
   * with statistics.
   */
  async cfgPaymentsBalancesList(...args: any[]): Promise<Models.PaginatedUserBalanceList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3], user: args[4] };
    }
    const response = await this.client.request('GET', "/cfg/payments/balances/", { params });
    return (response as any).results || [];
  }

  /**
   * User balance ViewSet: /api/balances/ Read-only access to user balances
   * with statistics.
   */
  async cfgPaymentsBalancesRetrieve(id: number): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', `/cfg/payments/balances/${id}/`);
    return response;
  }

  /**
   * Get balance analytics. GET /api/balances/analytics/?days=30
   */
  async cfgPaymentsBalancesAnalyticsRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/cfg/payments/balances/analytics/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsBalancesHealthRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/cfg/payments/balances/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsBalancesStatsRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/cfg/payments/balances/stats/");
    return response;
  }

  /**
   * Get balance summary for all users. GET /api/balances/summary/
   */
  async cfgPaymentsBalancesSummaryRetrieve(): Promise<Models.UserBalance> {
    const response = await this.client.request('GET', "/cfg/payments/balances/summary/");
    return response;
  }

  async cfgPaymentsCurrenciesList(currency_type?: string, is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedCurrencyListList[]>;
  async cfgPaymentsCurrenciesList(params?: { currency_type?: string; is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedCurrencyListList[]>;

  /**
   * Currency ViewSet: /api/currencies/ Read-only access to currency
   * information with conversion capabilities.
   */
  async cfgPaymentsCurrenciesList(...args: any[]): Promise<Models.PaginatedCurrencyListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency_type: args[0], is_active: args[1], ordering: args[2], page: args[3], page_size: args[4], search: args[5] };
    }
    const response = await this.client.request('GET', "/cfg/payments/currencies/", { params });
    return (response as any).results || [];
  }

  /**
   * Disable create action.
   */
  async cfgPaymentsCurrenciesCreate(): Promise<Models.Currency> {
    const response = await this.client.request('POST', "/cfg/payments/currencies/");
    return response;
  }

  /**
   * Currency ViewSet: /api/currencies/ Read-only access to currency
   * information with conversion capabilities.
   */
  async cfgPaymentsCurrenciesRetrieve(id: number): Promise<Models.Currency> {
    const response = await this.client.request('GET', `/cfg/payments/currencies/${id}/`);
    return response;
  }

  /**
   * Get networks for specific currency. GET /api/currencies/{id}/networks/
   */
  async cfgPaymentsCurrenciesNetworksRetrieve(id: number): Promise<Models.Currency> {
    const response = await this.client.request('GET', `/cfg/payments/currencies/${id}/networks/`);
    return response;
  }

  /**
   * Get providers supporting specific currency. GET
   * /api/currencies/{id}/providers/
   */
  async cfgPaymentsCurrenciesProvidersRetrieve(id: number): Promise<Models.Currency> {
    const response = await this.client.request('GET', `/cfg/payments/currencies/${id}/providers/`);
    return response;
  }

  /**
   * Convert between currencies. POST /api/currencies/convert/
   */
  async cfgPaymentsCurrenciesConvertCreate(): Promise<Models.Currency> {
    const response = await this.client.request('POST', "/cfg/payments/currencies/convert/");
    return response;
  }

  /**
   * Get only cryptocurrencies. GET /api/currencies/crypto/
   */
  async cfgPaymentsCurrenciesCryptoRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/cfg/payments/currencies/crypto/");
    return response;
  }

  /**
   * Get only fiat currencies. GET /api/currencies/fiat/
   */
  async cfgPaymentsCurrenciesFiatRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/cfg/payments/currencies/fiat/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsCurrenciesHealthRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/cfg/payments/currencies/health/");
    return response;
  }

  async cfgPaymentsCurrenciesRatesRetrieve(base_currency: string, currencies: string): Promise<Models.Currency>;
  async cfgPaymentsCurrenciesRatesRetrieve(params?: { base_currency: string; currencies: string }): Promise<Models.Currency>;

  /**
   * Get exchange rates
   * 
   * Get current exchange rates for specified currencies
   */
  async cfgPaymentsCurrenciesRatesRetrieve(...args: any[]): Promise<Models.Currency> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { base_currency: args[0], currencies: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/payments/currencies/rates/", { params });
    return response;
  }

  /**
   * Get only stablecoins. GET /api/currencies/stable/
   */
  async cfgPaymentsCurrenciesStableRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/cfg/payments/currencies/stable/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsCurrenciesStatsRetrieve(): Promise<Models.Currency> {
    const response = await this.client.request('GET', "/cfg/payments/currencies/stats/");
    return response;
  }

  async cfgPaymentsCurrenciesSupportedRetrieve(currency_type?: string, provider?: string): Promise<Models.Currency>;
  async cfgPaymentsCurrenciesSupportedRetrieve(params?: { currency_type?: string; provider?: string }): Promise<Models.Currency>;

  /**
   * Get supported currencies
   * 
   * Get list of supported currencies from payment providers
   */
  async cfgPaymentsCurrenciesSupportedRetrieve(...args: any[]): Promise<Models.Currency> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency_type: args[0], provider: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/payments/currencies/supported/", { params });
    return response;
  }

  async cfgPaymentsEndpointGroupsList(is_enabled?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedEndpointGroupList[]>;
  async cfgPaymentsEndpointGroupsList(params?: { is_enabled?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedEndpointGroupList[]>;

  /**
   * Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
   * endpoint group information.
   */
  async cfgPaymentsEndpointGroupsList(...args: any[]): Promise<Models.PaginatedEndpointGroupList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_enabled: args[0], ordering: args[1], page: args[2], page_size: args[3], search: args[4] };
    }
    const response = await this.client.request('GET', "/cfg/payments/endpoint-groups/", { params });
    return (response as any).results || [];
  }

  /**
   * Endpoint Group ViewSet: /api/endpoint-groups/ Read-only access to
   * endpoint group information.
   */
  async cfgPaymentsEndpointGroupsRetrieve(id: number): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', `/cfg/payments/endpoint-groups/${id}/`);
    return response;
  }

  /**
   * Get available endpoint groups for subscription. GET
   * /api/endpoint-groups/available/
   */
  async cfgPaymentsEndpointGroupsAvailableRetrieve(): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', "/cfg/payments/endpoint-groups/available/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsEndpointGroupsHealthRetrieve(): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', "/cfg/payments/endpoint-groups/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsEndpointGroupsStatsRetrieve(): Promise<Models.EndpointGroup> {
    const response = await this.client.request('GET', "/cfg/payments/endpoint-groups/stats/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsHealthRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/health/");
    return response;
  }

  async cfgPaymentsNetworksList(is_active?: boolean, native_currency__code?: string, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedNetworkList[]>;
  async cfgPaymentsNetworksList(params?: { is_active?: boolean; native_currency__code?: string; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedNetworkList[]>;

  /**
   * Network ViewSet: /api/networks/ Read-only access to blockchain network
   * information.
   */
  async cfgPaymentsNetworksList(...args: any[]): Promise<Models.PaginatedNetworkList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], native_currency__code: args[1], ordering: args[2], page: args[3], page_size: args[4], search: args[5] };
    }
    const response = await this.client.request('GET', "/cfg/payments/networks/", { params });
    return (response as any).results || [];
  }

  /**
   * Network ViewSet: /api/networks/ Read-only access to blockchain network
   * information.
   */
  async cfgPaymentsNetworksRetrieve(id: number): Promise<Models.Network> {
    const response = await this.client.request('GET', `/cfg/payments/networks/${id}/`);
    return response;
  }

  /**
   * Get networks grouped by currency. GET /api/networks/by_currency/
   */
  async cfgPaymentsNetworksByCurrencyRetrieve(): Promise<Models.Network> {
    const response = await this.client.request('GET', "/cfg/payments/networks/by_currency/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsNetworksHealthRetrieve(): Promise<Models.Network> {
    const response = await this.client.request('GET', "/cfg/payments/networks/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsNetworksStatsRetrieve(): Promise<Models.Network> {
    const response = await this.client.request('GET', "/cfg/payments/networks/stats/");
    return response;
  }

  /**
   * API Keys Overview
   * 
   * Get API keys overview
   */
  async cfgPaymentsOverviewDashboardApiKeysOverviewRetrieve(): Promise<Models.APIKeysOverview> {
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/api_keys_overview/");
    return response;
  }

  /**
   * Balance Overview
   * 
   * Get user balance overview
   */
  async cfgPaymentsOverviewDashboardBalanceOverviewRetrieve(): Promise<Models.BalanceOverview> {
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/balance_overview/");
    return response;
  }

  async cfgPaymentsOverviewDashboardChartDataRetrieve(period?: string): Promise<Models.PaymentsChartResponse>;
  async cfgPaymentsOverviewDashboardChartDataRetrieve(params?: { period?: string }): Promise<Models.PaymentsChartResponse>;

  /**
   * Payments Chart Data
   * 
   * Get chart data for payments visualization
   */
  async cfgPaymentsOverviewDashboardChartDataRetrieve(...args: any[]): Promise<Models.PaymentsChartResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { period: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/chart_data/", { params });
    return response;
  }

  /**
   * Payments Dashboard Metrics
   * 
   * Get payments dashboard metrics including balance, subscriptions, API
   * keys, and payments
   */
  async cfgPaymentsOverviewDashboardMetricsRetrieve(): Promise<Models.PaymentsMetrics> {
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/metrics/");
    return response;
  }

  /**
   * Payments Dashboard Overview
   * 
   * Get complete payments dashboard overview with metrics, recent payments,
   * and analytics
   */
  async cfgPaymentsOverviewDashboardOverviewRetrieve(): Promise<Models.PaymentsDashboardOverview> {
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/overview/");
    return response;
  }

  async cfgPaymentsOverviewDashboardPaymentAnalyticsRetrieve(limit?: number): Promise<Models.PaymentAnalyticsResponse>;
  async cfgPaymentsOverviewDashboardPaymentAnalyticsRetrieve(params?: { limit?: number }): Promise<Models.PaymentAnalyticsResponse>;

  /**
   * Payment Analytics
   * 
   * Get analytics for payments by currency and provider
   */
  async cfgPaymentsOverviewDashboardPaymentAnalyticsRetrieve(...args: any[]): Promise<Models.PaymentAnalyticsResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/payment_analytics/", { params });
    return response;
  }

  async cfgPaymentsOverviewDashboardRecentPaymentsList(limit?: number, page?: number, page_size?: number): Promise<Models.PaginatedRecentPaymentList[]>;
  async cfgPaymentsOverviewDashboardRecentPaymentsList(params?: { limit?: number; page?: number; page_size?: number }): Promise<Models.PaginatedRecentPaymentList[]>;

  /**
   * Recent Payments
   * 
   * Get recent payments for the user
   */
  async cfgPaymentsOverviewDashboardRecentPaymentsList(...args: any[]): Promise<Models.PaginatedRecentPaymentList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0], page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/recent_payments/", { params });
    return (response as any).results || [];
  }

  async cfgPaymentsOverviewDashboardRecentTransactionsList(limit?: number, page?: number, page_size?: number): Promise<Models.PaginatedRecentTransactionList[]>;
  async cfgPaymentsOverviewDashboardRecentTransactionsList(params?: { limit?: number; page?: number; page_size?: number }): Promise<Models.PaginatedRecentTransactionList[]>;

  /**
   * Recent Transactions
   * 
   * Get recent balance transactions for the user
   */
  async cfgPaymentsOverviewDashboardRecentTransactionsList(...args: any[]): Promise<Models.PaginatedRecentTransactionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0], page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/recent_transactions/", { params });
    return (response as any).results || [];
  }

  /**
   * Subscription Overview
   * 
   * Get current subscription overview
   */
  async cfgPaymentsOverviewDashboardSubscriptionOverviewRetrieve(): Promise<Models.SubscriptionOverview> {
    const response = await this.client.request('GET', "/cfg/payments/overview/dashboard/subscription_overview/");
    return response;
  }

  async cfgPaymentsPaymentsList(currency__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string, status?: string, user?: number): Promise<Models.PaginatedPaymentListList[]>;
  async cfgPaymentsPaymentsList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number }): Promise<Models.PaginatedPaymentListList[]>;

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async cfgPaymentsPaymentsList(...args: any[]): Promise<Models.PaginatedPaymentListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency__code: args[0], ordering: args[1], page: args[2], page_size: args[3], provider: args[4], search: args[5], status: args[6], user: args[7] };
    }
    const response = await this.client.request('GET', "/cfg/payments/payments/", { params });
    return (response as any).results || [];
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async cfgPaymentsPaymentsCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', "/cfg/payments/payments/", { body: data });
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async cfgPaymentsPaymentsRetrieve(id: string): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/cfg/payments/payments/${id}/`);
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async cfgPaymentsPaymentsUpdate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PUT', `/cfg/payments/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async cfgPaymentsPaymentsPartialUpdate(id: string, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PATCH', `/cfg/payments/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * Global payment ViewSet: /api/v1/payments/ Provides admin-level access to
   * all payments with filtering and stats.
   */
  async cfgPaymentsPaymentsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/payments/${id}/`);
    return;
  }

  /**
   * Cancel payment. POST /api/v1/payments/{id}/cancel/
   */
  async cfgPaymentsPaymentsCancelCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/cfg/payments/payments/${id}/cancel/`, { body: data });
    return response;
  }

  /**
   * Check payment status with provider. POST
   * /api/v1/payments/{id}/check_status/
   */
  async cfgPaymentsPaymentsCheckStatusCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/cfg/payments/payments/${id}/check_status/`, { body: data });
    return response;
  }

  /**
   * Get payment analytics. GET /api/v1/payments/analytics/?days=30
   */
  async cfgPaymentsPaymentsAnalyticsRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/payments/analytics/");
    return response;
  }

  /**
   * Get payments grouped by provider. GET /api/v1/payments/by_provider/
   */
  async cfgPaymentsPaymentsByProviderRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/payments/by_provider/");
    return response;
  }

  /**
   * Standalone payment creation endpoint: /api/v1/payments/create/
   * Simplified endpoint for payment creation without full ViewSet overhead.
   */
  async cfgPaymentsPaymentsCreateCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', "/cfg/payments/payments/create/", { body: data });
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsPaymentsHealthRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/payments/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsPaymentsStatsRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/payments/stats/");
    return response;
  }

  /**
   * Standalone payment status endpoint: /api/v1/payments/{id}/status/ Quick
   * status check without full ViewSet overhead.
   */
  async cfgPaymentsPaymentsStatusRetrieve(id: string): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/cfg/payments/payments/status/${id}/`);
    return response;
  }

  async cfgPaymentsProviderCurrenciesList(currency__code?: string, is_enabled?: boolean, network__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string): Promise<Models.PaginatedProviderCurrencyList[]>;
  async cfgPaymentsProviderCurrenciesList(params?: { currency__code?: string; is_enabled?: boolean; network__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string }): Promise<Models.PaginatedProviderCurrencyList[]>;

  /**
   * Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
   * provider-specific currency information.
   */
  async cfgPaymentsProviderCurrenciesList(...args: any[]): Promise<Models.PaginatedProviderCurrencyList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency__code: args[0], is_enabled: args[1], network__code: args[2], ordering: args[3], page: args[4], page_size: args[5], provider: args[6], search: args[7] };
    }
    const response = await this.client.request('GET', "/cfg/payments/provider-currencies/", { params });
    return (response as any).results || [];
  }

  /**
   * Provider Currency ViewSet: /api/provider-currencies/ Read-only access to
   * provider-specific currency information.
   */
  async cfgPaymentsProviderCurrenciesRetrieve(id: number): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', `/cfg/payments/provider-currencies/${id}/`);
    return response;
  }

  /**
   * Get provider currencies grouped by provider. GET
   * /api/provider-currencies/by_provider/
   */
  async cfgPaymentsProviderCurrenciesByProviderRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/cfg/payments/provider-currencies/by_provider/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsProviderCurrenciesHealthRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/cfg/payments/provider-currencies/health/");
    return response;
  }

  /**
   * Get currency limits by provider. GET
   * /api/provider-currencies/limits/?provider=nowpayments
   */
  async cfgPaymentsProviderCurrenciesLimitsRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/cfg/payments/provider-currencies/limits/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsProviderCurrenciesStatsRetrieve(): Promise<Models.ProviderCurrency> {
    const response = await this.client.request('GET', "/cfg/payments/provider-currencies/stats/");
    return response;
  }

  async cfgPaymentsSubscriptionsList(ordering?: string, page?: number, page_size?: number, search?: string, status?: string, tier?: string, user?: number): Promise<Models.PaginatedSubscriptionListList[]>;
  async cfgPaymentsSubscriptionsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string; user?: number }): Promise<Models.PaginatedSubscriptionListList[]>;

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async cfgPaymentsSubscriptionsList(...args: any[]): Promise<Models.PaginatedSubscriptionListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3], status: args[4], tier: args[5], user: args[6] };
    }
    const response = await this.client.request('GET', "/cfg/payments/subscriptions/", { params });
    return (response as any).results || [];
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async cfgPaymentsSubscriptionsCreate(data: Models.SubscriptionCreateRequest): Promise<Models.SubscriptionCreate> {
    const response = await this.client.request('POST', "/cfg/payments/subscriptions/", { body: data });
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async cfgPaymentsSubscriptionsRetrieve(id: string): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/cfg/payments/subscriptions/${id}/`);
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async cfgPaymentsSubscriptionsUpdate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PUT', `/cfg/payments/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async cfgPaymentsSubscriptionsPartialUpdate(id: string, data?: Models.PatchedSubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PATCH', `/cfg/payments/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * Global subscription ViewSet: /api/subscriptions/ Provides admin-level
   * access to all subscriptions with filtering and stats.
   */
  async cfgPaymentsSubscriptionsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/subscriptions/${id}/`);
    return;
  }

  /**
   * Increment subscription usage. POST
   * /api/subscriptions/{id}/increment_usage/
   */
  async cfgPaymentsSubscriptionsIncrementUsageCreate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/cfg/payments/subscriptions/${id}/increment_usage/`, { body: data });
    return response;
  }

  /**
   * Update subscription status. POST /api/subscriptions/{id}/update_status/
   */
  async cfgPaymentsSubscriptionsUpdateStatusCreate(id: string, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/cfg/payments/subscriptions/${id}/update_status/`, { body: data });
    return response;
  }

  /**
   * Get subscription analytics. GET /api/subscriptions/analytics/?days=30
   */
  async cfgPaymentsSubscriptionsAnalyticsRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/cfg/payments/subscriptions/analytics/");
    return response;
  }

  /**
   * Get subscriptions grouped by status. GET /api/subscriptions/by_status/
   */
  async cfgPaymentsSubscriptionsByStatusRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/cfg/payments/subscriptions/by_status/");
    return response;
  }

  /**
   * Get subscriptions grouped by tier. GET /api/subscriptions/by_tier/
   */
  async cfgPaymentsSubscriptionsByTierRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/cfg/payments/subscriptions/by_tier/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsSubscriptionsHealthRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/cfg/payments/subscriptions/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsSubscriptionsStatsRetrieve(): Promise<Models.Subscription> {
    const response = await this.client.request('GET', "/cfg/payments/subscriptions/stats/");
    return response;
  }

  async cfgPaymentsTariffsList(is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedTariffList[]>;
  async cfgPaymentsTariffsList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedTariffList[]>;

  /**
   * Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
   * subscription selection.
   */
  async cfgPaymentsTariffsList(...args: any[]): Promise<Models.PaginatedTariffList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], ordering: args[1], page: args[2], page_size: args[3], search: args[4] };
    }
    const response = await this.client.request('GET', "/cfg/payments/tariffs/", { params });
    return (response as any).results || [];
  }

  /**
   * Tariff ViewSet: /api/tariffs/ Read-only access to tariff information for
   * subscription selection.
   */
  async cfgPaymentsTariffsRetrieve(id: number): Promise<Models.Tariff> {
    const response = await this.client.request('GET', `/cfg/payments/tariffs/${id}/`);
    return response;
  }

  /**
   * Get endpoint groups for specific tariff. GET
   * /api/tariffs/{id}/endpoint_groups/
   */
  async cfgPaymentsTariffsEndpointGroupsRetrieve(id: number): Promise<Models.Tariff> {
    const response = await this.client.request('GET', `/cfg/payments/tariffs/${id}/endpoint_groups/`);
    return response;
  }

  /**
   * Get free tariffs. GET /api/tariffs/free/
   */
  async cfgPaymentsTariffsFreeRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/cfg/payments/tariffs/free/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsTariffsHealthRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/cfg/payments/tariffs/health/");
    return response;
  }

  /**
   * Get paid tariffs. GET /api/tariffs/paid/
   */
  async cfgPaymentsTariffsPaidRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/cfg/payments/tariffs/paid/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsTariffsStatsRetrieve(): Promise<Models.Tariff> {
    const response = await this.client.request('GET', "/cfg/payments/tariffs/stats/");
    return response;
  }

  async cfgPaymentsTransactionsList(ordering?: string, page?: number, page_size?: number, payment_id?: string, search?: string, transaction_type?: string, user?: number): Promise<Models.PaginatedTransactionList[]>;
  async cfgPaymentsTransactionsList(params?: { ordering?: string; page?: number; page_size?: number; payment_id?: string; search?: string; transaction_type?: string; user?: number }): Promise<Models.PaginatedTransactionList[]>;

  /**
   * Transaction ViewSet: /api/transactions/ Read-only access to transaction
   * history with filtering.
   */
  async cfgPaymentsTransactionsList(...args: any[]): Promise<Models.PaginatedTransactionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], payment_id: args[3], search: args[4], transaction_type: args[5], user: args[6] };
    }
    const response = await this.client.request('GET', "/cfg/payments/transactions/", { params });
    return (response as any).results || [];
  }

  /**
   * Transaction ViewSet: /api/transactions/ Read-only access to transaction
   * history with filtering.
   */
  async cfgPaymentsTransactionsRetrieve(id: string): Promise<Models.Transaction> {
    const response = await this.client.request('GET', `/cfg/payments/transactions/${id}/`);
    return response;
  }

  /**
   * Get transactions grouped by type. GET /api/transactions/by_type/
   */
  async cfgPaymentsTransactionsByTypeRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/cfg/payments/transactions/by_type/");
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsTransactionsHealthRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/cfg/payments/transactions/health/");
    return response;
  }

  /**
   * Get recent transactions. GET /api/transactions/recent/?limit=10
   */
  async cfgPaymentsTransactionsRecentRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/cfg/payments/transactions/recent/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsTransactionsStatsRetrieve(): Promise<Models.Transaction> {
    const response = await this.client.request('GET', "/cfg/payments/transactions/stats/");
    return response;
  }

  async cfgPaymentsUsersList(currency__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string, status?: string): Promise<Models.PaginatedPaymentListList[]>;
  async cfgPaymentsUsersList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }): Promise<Models.PaginatedPaymentListList[]>;

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersList(...args: any[]): Promise<Models.PaginatedPaymentListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { currency__code: args[0], ordering: args[1], page: args[2], page_size: args[3], provider: args[4], search: args[5], status: args[6] };
    }
    const response = await this.client.request('GET', "/cfg/payments/users/", { params });
    return (response as any).results || [];
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersCreate(data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', "/cfg/payments/users/", { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersRetrieve(id: string): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/cfg/payments/users/${id}/`);
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersUpdate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PUT', `/cfg/payments/users/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersPartialUpdate(id: string, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PATCH', `/cfg/payments/users/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/users/${id}/`);
    return;
  }

  /**
   * Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
   */
  async cfgPaymentsUsersCancelCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/cfg/payments/users/${id}/cancel/`, { body: data });
    return response;
  }

  /**
   * Check payment status with provider. POST
   * /api/v1/users/{user_id}/payments/{id}/check_status/
   */
  async cfgPaymentsUsersCheckStatusCreate(id: string, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/cfg/payments/users/${id}/check_status/`, { body: data });
    return response;
  }

  async cfgPaymentsUsersApiKeysList(user_pk: number, is_active?: boolean, ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedAPIKeyListList[]>;
  async cfgPaymentsUsersApiKeysList(user_pk: number, params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedAPIKeyListList[]>;

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async cfgPaymentsUsersApiKeysList(...args: any[]): Promise<Models.PaginatedAPIKeyListList[]> {
    const user_pk = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { is_active: args[1], ordering: args[2], page: args[3], page_size: args[4], search: args[5] };
    }
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/api-keys/`, { params });
    return (response as any).results || [];
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async cfgPaymentsUsersApiKeysCreate(user_pk: number, data: Models.APIKeyCreateRequest): Promise<Models.APIKeyCreate> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/api-keys/`, { body: data });
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async cfgPaymentsUsersApiKeysRetrieve(id: string, user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/api-keys/${id}/`);
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async cfgPaymentsUsersApiKeysUpdate(id: string, user_pk: number, data: Models.APIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PUT', `/cfg/payments/users/${user_pk}/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async cfgPaymentsUsersApiKeysPartialUpdate(id: string, user_pk: number, data?: Models.PatchedAPIKeyUpdateRequest): Promise<Models.APIKeyUpdate> {
    const response = await this.client.request('PATCH', `/cfg/payments/users/${user_pk}/api-keys/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/ Provides
   * user-scoped access to API keys with full CRUD operations.
   */
  async cfgPaymentsUsersApiKeysDestroy(id: string, user_pk: number): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/users/${user_pk}/api-keys/${id}/`);
    return;
  }

  /**
   * Perform action on API key. POST
   * /api/users/{user_id}/api-keys/{id}/perform_action/
   */
  async cfgPaymentsUsersApiKeysPerformActionCreate(id: string, user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/api-keys/${id}/perform_action/`);
    return response;
  }

  /**
   * Get user's active API keys. GET /api/users/{user_id}/api-keys/active/
   */
  async cfgPaymentsUsersApiKeysActiveRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/api-keys/active/`);
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsUsersApiKeysHealthRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/api-keys/health/`);
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsUsersApiKeysStatsRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/api-keys/stats/`);
    return response;
  }

  /**
   * Get user API key summary. GET /api/users/{user_id}/api-keys/summary/
   */
  async cfgPaymentsUsersApiKeysSummaryRetrieve(user_pk: number): Promise<Models.APIKeyDetail> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/api-keys/summary/`);
    return response;
  }

  async cfgPaymentsUsersPaymentsList(user_pk: number, currency__code?: string, ordering?: string, page?: number, page_size?: number, provider?: string, search?: string, status?: string): Promise<Models.PaginatedPaymentListList[]>;
  async cfgPaymentsUsersPaymentsList(user_pk: number, params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }): Promise<Models.PaginatedPaymentListList[]>;

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersPaymentsList(...args: any[]): Promise<Models.PaginatedPaymentListList[]> {
    const user_pk = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { currency__code: args[1], ordering: args[2], page: args[3], page_size: args[4], provider: args[5], search: args[6], status: args[7] };
    }
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/payments/`, { params });
    return (response as any).results || [];
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersPaymentsCreate(user_pk: number, data: Models.PaymentCreateRequest): Promise<Models.PaymentCreate> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/payments/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersPaymentsRetrieve(id: string, user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/payments/${id}/`);
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersPaymentsUpdate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PUT', `/cfg/payments/users/${user_pk}/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersPaymentsPartialUpdate(id: string, user_pk: number, data?: Models.PatchedPaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('PATCH', `/cfg/payments/users/${user_pk}/payments/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
   * Provides user-scoped access to payments with full CRUD operations.
   */
  async cfgPaymentsUsersPaymentsDestroy(id: string, user_pk: number): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/users/${user_pk}/payments/${id}/`);
    return;
  }

  /**
   * Cancel payment. POST /api/v1/users/{user_id}/payments/{id}/cancel/
   */
  async cfgPaymentsUsersPaymentsCancelCreate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/payments/${id}/cancel/`, { body: data });
    return response;
  }

  /**
   * Check payment status with provider. POST
   * /api/v1/users/{user_id}/payments/{id}/check_status/
   */
  async cfgPaymentsUsersPaymentsCheckStatusCreate(id: string, user_pk: number, data: Models.PaymentRequest): Promise<Models.Payment> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/payments/${id}/check_status/`, { body: data });
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsUsersPaymentsHealthRetrieve(user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/payments/health/`);
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsUsersPaymentsStatsRetrieve(user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/payments/stats/`);
    return response;
  }

  /**
   * Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
   */
  async cfgPaymentsUsersPaymentsSummaryRetrieve(user_pk: number): Promise<Models.Payment> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/payments/summary/`);
    return response;
  }

  async cfgPaymentsUsersSubscriptionsList(user_pk: number, ordering?: string, page?: number, page_size?: number, search?: string, status?: string, tier?: string): Promise<Models.PaginatedSubscriptionListList[]>;
  async cfgPaymentsUsersSubscriptionsList(user_pk: number, params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string }): Promise<Models.PaginatedSubscriptionListList[]>;

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async cfgPaymentsUsersSubscriptionsList(...args: any[]): Promise<Models.PaginatedSubscriptionListList[]> {
    const user_pk = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { ordering: args[1], page: args[2], page_size: args[3], search: args[4], status: args[5], tier: args[6] };
    }
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/subscriptions/`, { params });
    return (response as any).results || [];
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async cfgPaymentsUsersSubscriptionsCreate(user_pk: number, data: Models.SubscriptionCreateRequest): Promise<Models.SubscriptionCreate> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/subscriptions/`, { body: data });
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async cfgPaymentsUsersSubscriptionsRetrieve(id: string, user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/subscriptions/${id}/`);
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async cfgPaymentsUsersSubscriptionsUpdate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PUT', `/cfg/payments/users/${user_pk}/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async cfgPaymentsUsersSubscriptionsPartialUpdate(id: string, user_pk: number, data?: Models.PatchedSubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('PATCH', `/cfg/payments/users/${user_pk}/subscriptions/${id}/`, { body: data });
    return response;
  }

  /**
   * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
   * Provides user-scoped access to subscriptions with full CRUD operations.
   */
  async cfgPaymentsUsersSubscriptionsDestroy(id: string, user_pk: number): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/payments/users/${user_pk}/subscriptions/${id}/`);
    return;
  }

  /**
   * Increment subscription usage. POST
   * /api/users/{user_id}/subscriptions/{id}/increment_usage/
   */
  async cfgPaymentsUsersSubscriptionsIncrementUsageCreate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/subscriptions/${id}/increment_usage/`, { body: data });
    return response;
  }

  /**
   * Update subscription status. POST
   * /api/users/{user_id}/subscriptions/{id}/update_status/
   */
  async cfgPaymentsUsersSubscriptionsUpdateStatusCreate(id: string, user_pk: number, data: Models.SubscriptionRequest): Promise<Models.Subscription> {
    const response = await this.client.request('POST', `/cfg/payments/users/${user_pk}/subscriptions/${id}/update_status/`, { body: data });
    return response;
  }

  /**
   * Get user's active subscription. GET
   * /api/users/{user_id}/subscriptions/active/
   */
  async cfgPaymentsUsersSubscriptionsActiveRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/subscriptions/active/`);
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsUsersSubscriptionsHealthRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/subscriptions/health/`);
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsUsersSubscriptionsStatsRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/subscriptions/stats/`);
    return response;
  }

  /**
   * Get user subscription summary. GET
   * /api/users/{user_id}/subscriptions/summary/
   */
  async cfgPaymentsUsersSubscriptionsSummaryRetrieve(user_pk: number): Promise<Models.Subscription> {
    const response = await this.client.request('GET', `/cfg/payments/users/${user_pk}/subscriptions/summary/`);
    return response;
  }

  /**
   * Health check for the ViewSet and related services. Returns service
   * status and basic metrics.
   */
  async cfgPaymentsUsersHealthRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/users/health/");
    return response;
  }

  /**
   * Get statistics for the current queryset. Returns counts, aggregates, and
   * breakdowns.
   */
  async cfgPaymentsUsersStatsRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/users/stats/");
    return response;
  }

  /**
   * Get user payment summary. GET /api/v1/users/{user_id}/payments/summary/
   */
  async cfgPaymentsUsersSummaryRetrieve(): Promise<Models.Payment> {
    const response = await this.client.request('GET', "/cfg/payments/users/summary/");
    return response;
  }

}