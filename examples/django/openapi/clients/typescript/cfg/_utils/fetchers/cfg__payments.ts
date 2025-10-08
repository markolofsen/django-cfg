/**
 * Typed fetchers for Payments
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { APIKeyCreateSchema, type APIKeyCreate } from '../schemas/APIKeyCreate.schema'
import { APIKeyCreateRequestSchema, type APIKeyCreateRequest } from '../schemas/APIKeyCreateRequest.schema'
import { APIKeyDetailSchema, type APIKeyDetail } from '../schemas/APIKeyDetail.schema'
import { APIKeyUpdateSchema, type APIKeyUpdate } from '../schemas/APIKeyUpdate.schema'
import { APIKeyUpdateRequestSchema, type APIKeyUpdateRequest } from '../schemas/APIKeyUpdateRequest.schema'
import { APIKeyValidationRequestSchema, type APIKeyValidationRequest } from '../schemas/APIKeyValidationRequest.schema'
import { APIKeyValidationResponseSchema, type APIKeyValidationResponse } from '../schemas/APIKeyValidationResponse.schema'
import { APIKeysOverviewSchema, type APIKeysOverview } from '../schemas/APIKeysOverview.schema'
import { BalanceOverviewSchema, type BalanceOverview } from '../schemas/BalanceOverview.schema'
import { CurrencySchema, type Currency } from '../schemas/Currency.schema'
import { EndpointGroupSchema, type EndpointGroup } from '../schemas/EndpointGroup.schema'
import { NetworkSchema, type Network } from '../schemas/Network.schema'
import { PaginatedAPIKeyListListSchema, type PaginatedAPIKeyListList } from '../schemas/PaginatedAPIKeyListList.schema'
import { PaginatedCurrencyListListSchema, type PaginatedCurrencyListList } from '../schemas/PaginatedCurrencyListList.schema'
import { PaginatedEndpointGroupListSchema, type PaginatedEndpointGroupList } from '../schemas/PaginatedEndpointGroupList.schema'
import { PaginatedNetworkListSchema, type PaginatedNetworkList } from '../schemas/PaginatedNetworkList.schema'
import { PaginatedPaymentListListSchema, type PaginatedPaymentListList } from '../schemas/PaginatedPaymentListList.schema'
import { PaginatedProviderCurrencyListSchema, type PaginatedProviderCurrencyList } from '../schemas/PaginatedProviderCurrencyList.schema'
import { PaginatedRecentPaymentListSchema, type PaginatedRecentPaymentList } from '../schemas/PaginatedRecentPaymentList.schema'
import { PaginatedRecentTransactionListSchema, type PaginatedRecentTransactionList } from '../schemas/PaginatedRecentTransactionList.schema'
import { PaginatedSubscriptionListListSchema, type PaginatedSubscriptionListList } from '../schemas/PaginatedSubscriptionListList.schema'
import { PaginatedTariffListSchema, type PaginatedTariffList } from '../schemas/PaginatedTariffList.schema'
import { PaginatedTransactionListSchema, type PaginatedTransactionList } from '../schemas/PaginatedTransactionList.schema'
import { PaginatedUserBalanceListSchema, type PaginatedUserBalanceList } from '../schemas/PaginatedUserBalanceList.schema'
import { PaymentSchema, type Payment } from '../schemas/Payment.schema'
import { PaymentAnalyticsResponseSchema, type PaymentAnalyticsResponse } from '../schemas/PaymentAnalyticsResponse.schema'
import { PaymentCreateSchema, type PaymentCreate } from '../schemas/PaymentCreate.schema'
import { PaymentCreateRequestSchema, type PaymentCreateRequest } from '../schemas/PaymentCreateRequest.schema'
import { PaymentRequestSchema, type PaymentRequest } from '../schemas/PaymentRequest.schema'
import { PaymentsChartResponseSchema, type PaymentsChartResponse } from '../schemas/PaymentsChartResponse.schema'
import { PaymentsDashboardOverviewSchema, type PaymentsDashboardOverview } from '../schemas/PaymentsDashboardOverview.schema'
import { PaymentsMetricsSchema, type PaymentsMetrics } from '../schemas/PaymentsMetrics.schema'
import { ProviderCurrencySchema, type ProviderCurrency } from '../schemas/ProviderCurrency.schema'
import { SubscriptionSchema, type Subscription } from '../schemas/Subscription.schema'
import { SubscriptionCreateSchema, type SubscriptionCreate } from '../schemas/SubscriptionCreate.schema'
import { SubscriptionCreateRequestSchema, type SubscriptionCreateRequest } from '../schemas/SubscriptionCreateRequest.schema'
import { SubscriptionOverviewSchema, type SubscriptionOverview } from '../schemas/SubscriptionOverview.schema'
import { SubscriptionRequestSchema, type SubscriptionRequest } from '../schemas/SubscriptionRequest.schema'
import { TariffSchema, type Tariff } from '../schemas/Tariff.schema'
import { TransactionSchema, type Transaction } from '../schemas/Transaction.schema'
import { UserBalanceSchema, type UserBalance } from '../schemas/UserBalance.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * getPaymentsApiKeysList
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method GET
 * @path /payments/api-keys/
 */
export async function getPaymentsApiKeysList(
  params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; user?: number },
  client?: API
): Promise<PaginatedAPIKeyListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysList(params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search, params?.user)
  return PaginatedAPIKeyListListSchema.parse(response)
}

/**
 * createPaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method POST
 * @path /payments/api-keys/
 */
export async function createPaymentsApiKeys(
  data: APIKeyCreateRequest,
  client?: API
): Promise<APIKeyCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysCreate(data)
  return APIKeyCreateSchema.parse(response)
}

/**
 * getPaymentsApiKeysById
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method GET
 * @path /payments/api-keys/{id}/
 */
export async function getPaymentsApiKeysById(
  id: string,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysRetrieve(id)
  return APIKeyDetailSchema.parse(response)
}

/**
 * updatePaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method PUT
 * @path /payments/api-keys/{id}/
 */
export async function updatePaymentsApiKeys(
  id: string, data: APIKeyUpdateRequest,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysUpdate(id, data)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * partialUpdatePaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method PATCH
 * @path /payments/api-keys/{id}/
 */
export async function partialUpdatePaymentsApiKeys(
  id: string,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysPartialUpdate(id)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * deletePaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method DELETE
 * @path /payments/api-keys/{id}/
 */
export async function deletePaymentsApiKeys(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysDestroy(id)
  return response
}

/**
 * createPaymentsApiKeysPerformAction
 *
 * Perform action on API key.
 * 
 * POST /api/api-keys/{id}/perform_action/
 *
 * @method POST
 * @path /payments/api-keys/{id}/perform_action/
 */
export async function createPaymentsApiKeysPerformAction(
  id: string,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysPerformActionCreate(id)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsApiKeysAnalyticsById
 *
 * Get API key analytics.
 * 
 * GET /api/api-keys/analytics/?days=30
 *
 * @method GET
 * @path /payments/api-keys/analytics/
 */
export async function getPaymentsApiKeysAnalyticsById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysAnalyticsRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsApiKeysByUserById
 *
 * Get API keys grouped by user.
 * 
 * GET /api/api-keys/by_user/
 *
 * @method GET
 * @path /payments/api-keys/by_user/
 */
export async function getPaymentsApiKeysByUserById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysByUserRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * createPaymentsApiKeysCreate
 *
 * Standalone API key creation endpoint: /api/api-keys/create/
 * 
 * Simplified endpoint for API key creation.
 *
 * @method POST
 * @path /payments/api-keys/create/
 */
export async function createPaymentsApiKeysCreate(
  data: APIKeyCreateRequest,
  client?: API
): Promise<APIKeyCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysCreateCreate(data)
  return APIKeyCreateSchema.parse(response)
}

/**
 * getPaymentsApiKeysExpiringSoonById
 *
 * Get API keys expiring soon.
 * 
 * GET /api/api-keys/expiring_soon/?days=7
 *
 * @method GET
 * @path /payments/api-keys/expiring_soon/
 */
export async function getPaymentsApiKeysExpiringSoonById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysExpiringSoonRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsApiKeysHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/api-keys/health/
 */
export async function getPaymentsApiKeysHealthById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysHealthRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsApiKeysStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/api-keys/stats/
 */
export async function getPaymentsApiKeysStatsById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysStatsRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * Validate API Key (Standalone)
 *
 * Standalone endpoint to validate an API key and return key information
 *
 * @method POST
 * @path /payments/api-keys/validate/
 */
export async function createPaymentsApiKeysValidate(
  data: APIKeyValidationRequest,
  client?: API
): Promise<APIKeyValidationResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysValidateCreate(data)
  return APIKeyValidationResponseSchema.parse(response)
}

/**
 * Validate API Key
 *
 * Validate an API key and return key information
 *
 * @method POST
 * @path /payments/api-keys/validate_key/
 */
export async function createPaymentsApiKeysValidateKey(
  data: APIKeyValidationRequest,
  client?: API
): Promise<APIKeyValidationResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.apiKeysValidateKeyCreate(data)
  return APIKeyValidationResponseSchema.parse(response)
}

/**
 * getPaymentsBalancesList
 *
 * User balance ViewSet: /api/balances/
 * 
 * Read-only access to user balances with statistics.
 *
 * @method GET
 * @path /payments/balances/
 */
export async function getPaymentsBalancesList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string; user?: number },
  client?: API
): Promise<PaginatedUserBalanceList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.balancesList(params?.ordering, params?.page, params?.page_size, params?.search, params?.user)
  return PaginatedUserBalanceListSchema.parse(response)
}

/**
 * getPaymentsBalancesById
 *
 * User balance ViewSet: /api/balances/
 * 
 * Read-only access to user balances with statistics.
 *
 * @method GET
 * @path /payments/balances/{id}/
 */
export async function getPaymentsBalancesById(
  id: number,
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.balancesRetrieve(id)
  return UserBalanceSchema.parse(response)
}

/**
 * getPaymentsBalancesAnalyticsById
 *
 * Get balance analytics.
 * 
 * GET /api/balances/analytics/?days=30
 *
 * @method GET
 * @path /payments/balances/analytics/
 */
export async function getPaymentsBalancesAnalyticsById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.balancesAnalyticsRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getPaymentsBalancesHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/balances/health/
 */
export async function getPaymentsBalancesHealthById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.balancesHealthRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getPaymentsBalancesStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/balances/stats/
 */
export async function getPaymentsBalancesStatsById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.balancesStatsRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getPaymentsBalancesSummaryById
 *
 * Get balance summary for all users.
 * 
 * GET /api/balances/summary/
 *
 * @method GET
 * @path /payments/balances/summary/
 */
export async function getPaymentsBalancesSummaryById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.balancesSummaryRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getPaymentsCurrenciesList
 *
 * Currency ViewSet: /api/currencies/
 * 
 * Read-only access to currency information with conversion capabilities.
 *
 * @method GET
 * @path /payments/currencies/
 */
export async function getPaymentsCurrenciesList(
  params?: { currency_type?: string; is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedCurrencyListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesList(params?.currency_type, params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedCurrencyListListSchema.parse(response)
}

/**
 * createPaymentsCurrencies
 *
 * Disable create action.
 *
 * @method POST
 * @path /payments/currencies/
 */
export async function createPaymentsCurrencies(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesCreate()
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesById
 *
 * Currency ViewSet: /api/currencies/
 * 
 * Read-only access to currency information with conversion capabilities.
 *
 * @method GET
 * @path /payments/currencies/{id}/
 */
export async function getPaymentsCurrenciesById(
  id: number,
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesRetrieve(id)
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesNetworksById
 *
 * Get networks for specific currency.
 * 
 * GET /api/currencies/{id}/networks/
 *
 * @method GET
 * @path /payments/currencies/{id}/networks/
 */
export async function getPaymentsCurrenciesNetworksById(
  id: number,
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesNetworksRetrieve(id)
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesProvidersById
 *
 * Get providers supporting specific currency.
 * 
 * GET /api/currencies/{id}/providers/
 *
 * @method GET
 * @path /payments/currencies/{id}/providers/
 */
export async function getPaymentsCurrenciesProvidersById(
  id: number,
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesProvidersRetrieve(id)
  return CurrencySchema.parse(response)
}

/**
 * createPaymentsCurrenciesConvert
 *
 * Convert between currencies.
 * 
 * POST /api/currencies/convert/
 *
 * @method POST
 * @path /payments/currencies/convert/
 */
export async function createPaymentsCurrenciesConvert(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesConvertCreate()
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesCryptoById
 *
 * Get only cryptocurrencies.
 * 
 * GET /api/currencies/crypto/
 *
 * @method GET
 * @path /payments/currencies/crypto/
 */
export async function getPaymentsCurrenciesCryptoById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesCryptoRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesFiatById
 *
 * Get only fiat currencies.
 * 
 * GET /api/currencies/fiat/
 *
 * @method GET
 * @path /payments/currencies/fiat/
 */
export async function getPaymentsCurrenciesFiatById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesFiatRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/currencies/health/
 */
export async function getPaymentsCurrenciesHealthById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesHealthRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * Get exchange rates
 *
 * Get current exchange rates for specified currencies
 *
 * @method GET
 * @path /payments/currencies/rates/
 */
export async function getPaymentsCurrenciesRatesById(
  params: { base_currency: string; currencies: string },
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesRatesRetrieve(params.base_currency, params.currencies)
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesStableById
 *
 * Get only stablecoins.
 * 
 * GET /api/currencies/stable/
 *
 * @method GET
 * @path /payments/currencies/stable/
 */
export async function getPaymentsCurrenciesStableById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesStableRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsCurrenciesStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/currencies/stats/
 */
export async function getPaymentsCurrenciesStatsById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesStatsRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * Get supported currencies
 *
 * Get list of supported currencies from payment providers
 *
 * @method GET
 * @path /payments/currencies/supported/
 */
export async function getPaymentsCurrenciesSupportedById(
  params?: { currency_type?: string; provider?: string },
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.currenciesSupportedRetrieve(params?.currency_type, params?.provider)
  return CurrencySchema.parse(response)
}

/**
 * getPaymentsEndpointGroupsList
 *
 * Endpoint Group ViewSet: /api/endpoint-groups/
 * 
 * Read-only access to endpoint group information.
 *
 * @method GET
 * @path /payments/endpoint-groups/
 */
export async function getPaymentsEndpointGroupsList(
  params?: { is_enabled?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedEndpointGroupList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.endpointGroupsList(params?.is_enabled, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedEndpointGroupListSchema.parse(response)
}

/**
 * getPaymentsEndpointGroupsById
 *
 * Endpoint Group ViewSet: /api/endpoint-groups/
 * 
 * Read-only access to endpoint group information.
 *
 * @method GET
 * @path /payments/endpoint-groups/{id}/
 */
export async function getPaymentsEndpointGroupsById(
  id: number,
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.endpointGroupsRetrieve(id)
  return EndpointGroupSchema.parse(response)
}

/**
 * getPaymentsEndpointGroupsAvailableById
 *
 * Get available endpoint groups for subscription.
 * 
 * GET /api/endpoint-groups/available/
 *
 * @method GET
 * @path /payments/endpoint-groups/available/
 */
export async function getPaymentsEndpointGroupsAvailableById(
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.endpointGroupsAvailableRetrieve()
  return EndpointGroupSchema.parse(response)
}

/**
 * getPaymentsEndpointGroupsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/endpoint-groups/health/
 */
export async function getPaymentsEndpointGroupsHealthById(
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.endpointGroupsHealthRetrieve()
  return EndpointGroupSchema.parse(response)
}

/**
 * getPaymentsEndpointGroupsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/endpoint-groups/stats/
 */
export async function getPaymentsEndpointGroupsStatsById(
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.endpointGroupsStatsRetrieve()
  return EndpointGroupSchema.parse(response)
}

/**
 * getPaymentsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/health/
 */
export async function getPaymentsHealthById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.healthRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsNetworksList
 *
 * Network ViewSet: /api/networks/
 * 
 * Read-only access to blockchain network information.
 *
 * @method GET
 * @path /payments/networks/
 */
export async function getPaymentsNetworksList(
  params?: { is_active?: boolean; native_currency__code?: string; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedNetworkList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.networksList(params?.is_active, params?.native_currency__code, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedNetworkListSchema.parse(response)
}

/**
 * getPaymentsNetworksById
 *
 * Network ViewSet: /api/networks/
 * 
 * Read-only access to blockchain network information.
 *
 * @method GET
 * @path /payments/networks/{id}/
 */
export async function getPaymentsNetworksById(
  id: number,
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.networksRetrieve(id)
  return NetworkSchema.parse(response)
}

/**
 * getPaymentsNetworksByCurrencyById
 *
 * Get networks grouped by currency.
 * 
 * GET /api/networks/by_currency/
 *
 * @method GET
 * @path /payments/networks/by_currency/
 */
export async function getPaymentsNetworksByCurrencyById(
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.networksByCurrencyRetrieve()
  return NetworkSchema.parse(response)
}

/**
 * getPaymentsNetworksHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/networks/health/
 */
export async function getPaymentsNetworksHealthById(
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.networksHealthRetrieve()
  return NetworkSchema.parse(response)
}

/**
 * getPaymentsNetworksStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/networks/stats/
 */
export async function getPaymentsNetworksStatsById(
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.networksStatsRetrieve()
  return NetworkSchema.parse(response)
}

/**
 * API Keys Overview
 *
 * Get API keys overview
 *
 * @method GET
 * @path /payments/overview/dashboard/api_keys_overview/
 */
export async function getPaymentsOverviewDashboardApiKeysOverviewById(
  client?: API
): Promise<APIKeysOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardApiKeysOverviewRetrieve()
  return APIKeysOverviewSchema.parse(response)
}

/**
 * Balance Overview
 *
 * Get user balance overview
 *
 * @method GET
 * @path /payments/overview/dashboard/balance_overview/
 */
export async function getPaymentsOverviewDashboardBalanceOverviewById(
  client?: API
): Promise<BalanceOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardBalanceOverviewRetrieve()
  return BalanceOverviewSchema.parse(response)
}

/**
 * Payments Chart Data
 *
 * Get chart data for payments visualization
 *
 * @method GET
 * @path /payments/overview/dashboard/chart_data/
 */
export async function getPaymentsOverviewDashboardChartDataById(
  params?: { period?: string },
  client?: API
): Promise<PaymentsChartResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardChartDataRetrieve(params?.period)
  return PaymentsChartResponseSchema.parse(response)
}

/**
 * Payments Dashboard Metrics
 *
 * Get payments dashboard metrics including balance, subscriptions, API keys, and payments
 *
 * @method GET
 * @path /payments/overview/dashboard/metrics/
 */
export async function getPaymentsOverviewDashboardMetricsById(
  client?: API
): Promise<PaymentsMetrics> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardMetricsRetrieve()
  return PaymentsMetricsSchema.parse(response)
}

/**
 * Payments Dashboard Overview
 *
 * Get complete payments dashboard overview with metrics, recent payments, and analytics
 *
 * @method GET
 * @path /payments/overview/dashboard/overview/
 */
export async function getPaymentsOverviewDashboardOverviewById(
  client?: API
): Promise<PaymentsDashboardOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardOverviewRetrieve()
  return PaymentsDashboardOverviewSchema.parse(response)
}

/**
 * Payment Analytics
 *
 * Get analytics for payments by currency and provider
 *
 * @method GET
 * @path /payments/overview/dashboard/payment_analytics/
 */
export async function getPaymentsOverviewDashboardPaymentAnalyticsById(
  params?: { limit?: number },
  client?: API
): Promise<PaymentAnalyticsResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardPaymentAnalyticsRetrieve(params?.limit)
  return PaymentAnalyticsResponseSchema.parse(response)
}

/**
 * Recent Payments
 *
 * Get recent payments for the user
 *
 * @method GET
 * @path /payments/overview/dashboard/recent_payments/
 */
export async function getPaymentsOverviewDashboardRecentPaymentsList(
  params?: { limit?: number; page?: number; page_size?: number },
  client?: API
): Promise<PaginatedRecentPaymentList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardRecentPaymentsList(params?.limit, params?.page, params?.page_size)
  return PaginatedRecentPaymentListSchema.parse(response)
}

/**
 * Recent Transactions
 *
 * Get recent balance transactions for the user
 *
 * @method GET
 * @path /payments/overview/dashboard/recent_transactions/
 */
export async function getPaymentsOverviewDashboardRecentTransactionsList(
  params?: { limit?: number; page?: number; page_size?: number },
  client?: API
): Promise<PaginatedRecentTransactionList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardRecentTransactionsList(params?.limit, params?.page, params?.page_size)
  return PaginatedRecentTransactionListSchema.parse(response)
}

/**
 * Subscription Overview
 *
 * Get current subscription overview
 *
 * @method GET
 * @path /payments/overview/dashboard/subscription_overview/
 */
export async function getPaymentsOverviewDashboardSubscriptionOverviewById(
  client?: API
): Promise<SubscriptionOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.overviewDashboardSubscriptionOverviewRetrieve()
  return SubscriptionOverviewSchema.parse(response)
}

/**
 * getPaymentsPaymentsList
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method GET
 * @path /payments/payments/
 */
export async function getPaymentsPaymentsList(
  params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number },
  client?: API
): Promise<PaginatedPaymentListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsList(params?.currency__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search, params?.status, params?.user)
  return PaginatedPaymentListListSchema.parse(response)
}

/**
 * createPaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method POST
 * @path /payments/payments/
 */
export async function createPaymentsPayments(
  data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsCreate(data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getPaymentsPaymentsById
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method GET
 * @path /payments/payments/{id}/
 */
export async function getPaymentsPaymentsById(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsRetrieve(id)
  return PaymentSchema.parse(response)
}

/**
 * updatePaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method PUT
 * @path /payments/payments/{id}/
 */
export async function updatePaymentsPayments(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsUpdate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * partialUpdatePaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method PATCH
 * @path /payments/payments/{id}/
 */
export async function partialUpdatePaymentsPayments(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsPartialUpdate(id)
  return PaymentSchema.parse(response)
}

/**
 * deletePaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method DELETE
 * @path /payments/payments/{id}/
 */
export async function deletePaymentsPayments(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsDestroy(id)
  return response
}

/**
 * createPaymentsPaymentsCancel
 *
 * Cancel payment.
 * 
 * POST /api/v1/payments/{id}/cancel/
 *
 * @method POST
 * @path /payments/payments/{id}/cancel/
 */
export async function createPaymentsPaymentsCancel(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsCancelCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * createPaymentsPaymentsCheckStatus
 *
 * Check payment status with provider.
 * 
 * POST /api/v1/payments/{id}/check_status/
 *
 * @method POST
 * @path /payments/payments/{id}/check_status/
 */
export async function createPaymentsPaymentsCheckStatus(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsCheckStatusCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsPaymentsAnalyticsById
 *
 * Get payment analytics.
 * 
 * GET /api/v1/payments/analytics/?days=30
 *
 * @method GET
 * @path /payments/payments/analytics/
 */
export async function getPaymentsPaymentsAnalyticsById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsAnalyticsRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsPaymentsByProviderById
 *
 * Get payments grouped by provider.
 * 
 * GET /api/v1/payments/by_provider/
 *
 * @method GET
 * @path /payments/payments/by_provider/
 */
export async function getPaymentsPaymentsByProviderById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsByProviderRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * createPaymentsPaymentsCreate
 *
 * Standalone payment creation endpoint: /api/v1/payments/create/
 * 
 * Simplified endpoint for payment creation without full ViewSet overhead.
 *
 * @method POST
 * @path /payments/payments/create/
 */
export async function createPaymentsPaymentsCreate(
  data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsCreateCreate(data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getPaymentsPaymentsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/payments/health/
 */
export async function getPaymentsPaymentsHealthById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsHealthRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsPaymentsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/payments/stats/
 */
export async function getPaymentsPaymentsStatsById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsStatsRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsPaymentsStatusById
 *
 * Standalone payment status endpoint: /api/v1/payments/{id}/status/
 * 
 * Quick status check without full ViewSet overhead.
 *
 * @method GET
 * @path /payments/payments/status/{id}/
 */
export async function getPaymentsPaymentsStatusById(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.paymentsStatusRetrieve(id)
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsProviderCurrenciesList
 *
 * Provider Currency ViewSet: /api/provider-currencies/
 * 
 * Read-only access to provider-specific currency information.
 *
 * @method GET
 * @path /payments/provider-currencies/
 */
export async function getPaymentsProviderCurrenciesList(
  params?: { currency__code?: string; is_enabled?: boolean; network__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string },
  client?: API
): Promise<PaginatedProviderCurrencyList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.providerCurrenciesList(params?.currency__code, params?.is_enabled, params?.network__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search)
  return PaginatedProviderCurrencyListSchema.parse(response)
}

/**
 * getPaymentsProviderCurrenciesById
 *
 * Provider Currency ViewSet: /api/provider-currencies/
 * 
 * Read-only access to provider-specific currency information.
 *
 * @method GET
 * @path /payments/provider-currencies/{id}/
 */
export async function getPaymentsProviderCurrenciesById(
  id: number,
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.providerCurrenciesRetrieve(id)
  return ProviderCurrencySchema.parse(response)
}

/**
 * getPaymentsProviderCurrenciesByProviderById
 *
 * Get provider currencies grouped by provider.
 * 
 * GET /api/provider-currencies/by_provider/
 *
 * @method GET
 * @path /payments/provider-currencies/by_provider/
 */
export async function getPaymentsProviderCurrenciesByProviderById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.providerCurrenciesByProviderRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getPaymentsProviderCurrenciesHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/provider-currencies/health/
 */
export async function getPaymentsProviderCurrenciesHealthById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.providerCurrenciesHealthRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getPaymentsProviderCurrenciesLimitsById
 *
 * Get currency limits by provider.
 * 
 * GET /api/provider-currencies/limits/?provider=nowpayments
 *
 * @method GET
 * @path /payments/provider-currencies/limits/
 */
export async function getPaymentsProviderCurrenciesLimitsById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.providerCurrenciesLimitsRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getPaymentsProviderCurrenciesStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/provider-currencies/stats/
 */
export async function getPaymentsProviderCurrenciesStatsById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.providerCurrenciesStatsRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getPaymentsSubscriptionsList
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method GET
 * @path /payments/subscriptions/
 */
export async function getPaymentsSubscriptionsList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string; user?: number },
  client?: API
): Promise<PaginatedSubscriptionListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsList(params?.ordering, params?.page, params?.page_size, params?.search, params?.status, params?.tier, params?.user)
  return PaginatedSubscriptionListListSchema.parse(response)
}

/**
 * createPaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method POST
 * @path /payments/subscriptions/
 */
export async function createPaymentsSubscriptions(
  data: SubscriptionCreateRequest,
  client?: API
): Promise<SubscriptionCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsCreate(data)
  return SubscriptionCreateSchema.parse(response)
}

/**
 * getPaymentsSubscriptionsById
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method GET
 * @path /payments/subscriptions/{id}/
 */
export async function getPaymentsSubscriptionsById(
  id: string,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsRetrieve(id)
  return SubscriptionSchema.parse(response)
}

/**
 * updatePaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method PUT
 * @path /payments/subscriptions/{id}/
 */
export async function updatePaymentsSubscriptions(
  id: string, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsUpdate(id, data)
  return SubscriptionSchema.parse(response)
}

/**
 * partialUpdatePaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method PATCH
 * @path /payments/subscriptions/{id}/
 */
export async function partialUpdatePaymentsSubscriptions(
  id: string,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsPartialUpdate(id)
  return SubscriptionSchema.parse(response)
}

/**
 * deletePaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method DELETE
 * @path /payments/subscriptions/{id}/
 */
export async function deletePaymentsSubscriptions(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsDestroy(id)
  return response
}

/**
 * createPaymentsSubscriptionsIncrementUsage
 *
 * Increment subscription usage.
 * 
 * POST /api/subscriptions/{id}/increment_usage/
 *
 * @method POST
 * @path /payments/subscriptions/{id}/increment_usage/
 */
export async function createPaymentsSubscriptionsIncrementUsage(
  id: string, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsIncrementUsageCreate(id, data)
  return SubscriptionSchema.parse(response)
}

/**
 * createPaymentsSubscriptionsUpdateStatus
 *
 * Update subscription status.
 * 
 * POST /api/subscriptions/{id}/update_status/
 *
 * @method POST
 * @path /payments/subscriptions/{id}/update_status/
 */
export async function createPaymentsSubscriptionsUpdateStatus(
  id: string, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsUpdateStatusCreate(id, data)
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsSubscriptionsAnalyticsById
 *
 * Get subscription analytics.
 * 
 * GET /api/subscriptions/analytics/?days=30
 *
 * @method GET
 * @path /payments/subscriptions/analytics/
 */
export async function getPaymentsSubscriptionsAnalyticsById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsAnalyticsRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsSubscriptionsByStatusById
 *
 * Get subscriptions grouped by status.
 * 
 * GET /api/subscriptions/by_status/
 *
 * @method GET
 * @path /payments/subscriptions/by_status/
 */
export async function getPaymentsSubscriptionsByStatusById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsByStatusRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsSubscriptionsByTierById
 *
 * Get subscriptions grouped by tier.
 * 
 * GET /api/subscriptions/by_tier/
 *
 * @method GET
 * @path /payments/subscriptions/by_tier/
 */
export async function getPaymentsSubscriptionsByTierById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsByTierRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsSubscriptionsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/subscriptions/health/
 */
export async function getPaymentsSubscriptionsHealthById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsHealthRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsSubscriptionsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/subscriptions/stats/
 */
export async function getPaymentsSubscriptionsStatsById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.subscriptionsStatsRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsTariffsList
 *
 * Tariff ViewSet: /api/tariffs/
 * 
 * Read-only access to tariff information for subscription selection.
 *
 * @method GET
 * @path /payments/tariffs/
 */
export async function getPaymentsTariffsList(
  params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedTariffList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.tariffsList(params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedTariffListSchema.parse(response)
}

/**
 * getPaymentsTariffsById
 *
 * Tariff ViewSet: /api/tariffs/
 * 
 * Read-only access to tariff information for subscription selection.
 *
 * @method GET
 * @path /payments/tariffs/{id}/
 */
export async function getPaymentsTariffsById(
  id: number,
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.tariffsRetrieve(id)
  return TariffSchema.parse(response)
}

/**
 * getPaymentsTariffsEndpointGroupsById
 *
 * Get endpoint groups for specific tariff.
 * 
 * GET /api/tariffs/{id}/endpoint_groups/
 *
 * @method GET
 * @path /payments/tariffs/{id}/endpoint_groups/
 */
export async function getPaymentsTariffsEndpointGroupsById(
  id: number,
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.tariffsEndpointGroupsRetrieve(id)
  return TariffSchema.parse(response)
}

/**
 * getPaymentsTariffsFreeById
 *
 * Get free tariffs.
 * 
 * GET /api/tariffs/free/
 *
 * @method GET
 * @path /payments/tariffs/free/
 */
export async function getPaymentsTariffsFreeById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.tariffsFreeRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getPaymentsTariffsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/tariffs/health/
 */
export async function getPaymentsTariffsHealthById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.tariffsHealthRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getPaymentsTariffsPaidById
 *
 * Get paid tariffs.
 * 
 * GET /api/tariffs/paid/
 *
 * @method GET
 * @path /payments/tariffs/paid/
 */
export async function getPaymentsTariffsPaidById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.tariffsPaidRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getPaymentsTariffsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/tariffs/stats/
 */
export async function getPaymentsTariffsStatsById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.tariffsStatsRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getPaymentsTransactionsList
 *
 * Transaction ViewSet: /api/transactions/
 * 
 * Read-only access to transaction history with filtering.
 *
 * @method GET
 * @path /payments/transactions/
 */
export async function getPaymentsTransactionsList(
  params?: { ordering?: string; page?: number; page_size?: number; payment_id?: string; search?: string; transaction_type?: string; user?: number },
  client?: API
): Promise<PaginatedTransactionList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.transactionsList(params?.ordering, params?.page, params?.page_size, params?.payment_id, params?.search, params?.transaction_type, params?.user)
  return PaginatedTransactionListSchema.parse(response)
}

/**
 * getPaymentsTransactionsById
 *
 * Transaction ViewSet: /api/transactions/
 * 
 * Read-only access to transaction history with filtering.
 *
 * @method GET
 * @path /payments/transactions/{id}/
 */
export async function getPaymentsTransactionsById(
  id: string,
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.transactionsRetrieve(id)
  return TransactionSchema.parse(response)
}

/**
 * getPaymentsTransactionsByTypeById
 *
 * Get transactions grouped by type.
 * 
 * GET /api/transactions/by_type/
 *
 * @method GET
 * @path /payments/transactions/by_type/
 */
export async function getPaymentsTransactionsByTypeById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.transactionsByTypeRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getPaymentsTransactionsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/transactions/health/
 */
export async function getPaymentsTransactionsHealthById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.transactionsHealthRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getPaymentsTransactionsRecentById
 *
 * Get recent transactions.
 * 
 * GET /api/transactions/recent/?limit=10
 *
 * @method GET
 * @path /payments/transactions/recent/
 */
export async function getPaymentsTransactionsRecentById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.transactionsRecentRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getPaymentsTransactionsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/transactions/stats/
 */
export async function getPaymentsTransactionsStatsById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.transactionsStatsRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getPaymentsUsersList
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/
 */
export async function getPaymentsUsersList(
  params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string },
  client?: API
): Promise<PaginatedPaymentListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersList(params?.currency__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search, params?.status)
  return PaginatedPaymentListListSchema.parse(response)
}

/**
 * createPaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method POST
 * @path /payments/users/
 */
export async function createPaymentsUsers(
  data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersCreate(data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getPaymentsUsersById
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/{id}/
 */
export async function getPaymentsUsersById(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersRetrieve(id)
  return PaymentSchema.parse(response)
}

/**
 * updatePaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PUT
 * @path /payments/users/{id}/
 */
export async function updatePaymentsUsers(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersUpdate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * partialUpdatePaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PATCH
 * @path /payments/users/{id}/
 */
export async function partialUpdatePaymentsUsers(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPartialUpdate(id)
  return PaymentSchema.parse(response)
}

/**
 * deletePaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method DELETE
 * @path /payments/users/{id}/
 */
export async function deletePaymentsUsers(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersDestroy(id)
  return response
}

/**
 * createPaymentsUsersCancel
 *
 * Cancel payment.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/cancel/
 *
 * @method POST
 * @path /payments/users/{id}/cancel/
 */
export async function createPaymentsUsersCancel(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersCancelCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * createPaymentsUsersCheckStatus
 *
 * Check payment status with provider.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/check_status/
 *
 * @method POST
 * @path /payments/users/{id}/check_status/
 */
export async function createPaymentsUsersCheckStatus(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersCheckStatusCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsUsersApiKeysList
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/
 */
export async function getPaymentsUsersApiKeysList(
  user_pk: number, params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedAPIKeyListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysList(user_pk, params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedAPIKeyListListSchema.parse(response)
}

/**
 * createPaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method POST
 * @path /payments/users/{user_pk}/api-keys/
 */
export async function createPaymentsUsersApiKeys(
  user_pk: number, data: APIKeyCreateRequest,
  client?: API
): Promise<APIKeyCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysCreate(user_pk, data)
  return APIKeyCreateSchema.parse(response)
}

/**
 * getPaymentsUsersApiKeysById
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export async function getPaymentsUsersApiKeysById(
  id: string, user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysRetrieve(id, user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * updatePaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method PUT
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export async function updatePaymentsUsersApiKeys(
  id: string, user_pk: number, data: APIKeyUpdateRequest,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysUpdate(id, user_pk, data)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * partialUpdatePaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method PATCH
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export async function partialUpdatePaymentsUsersApiKeys(
  id: string, user_pk: number,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysPartialUpdate(id, user_pk)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * deletePaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method DELETE
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export async function deletePaymentsUsersApiKeys(
  id: string, user_pk: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysDestroy(id, user_pk)
  return response
}

/**
 * createPaymentsUsersApiKeysPerformAction
 *
 * Perform action on API key.
 * 
 * POST /api/users/{user_id}/api-keys/{id}/perform_action/
 *
 * @method POST
 * @path /payments/users/{user_pk}/api-keys/{id}/perform_action/
 */
export async function createPaymentsUsersApiKeysPerformAction(
  id: string, user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysPerformActionCreate(id, user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsUsersApiKeysActiveById
 *
 * Get user's active API keys.
 * 
 * GET /api/users/{user_id}/api-keys/active/
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/active/
 */
export async function getPaymentsUsersApiKeysActiveById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysActiveRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsUsersApiKeysHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/health/
 */
export async function getPaymentsUsersApiKeysHealthById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysHealthRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsUsersApiKeysStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/stats/
 */
export async function getPaymentsUsersApiKeysStatsById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysStatsRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsUsersApiKeysSummaryById
 *
 * Get user API key summary.
 * 
 * GET /api/users/{user_id}/api-keys/summary/
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/summary/
 */
export async function getPaymentsUsersApiKeysSummaryById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersApiKeysSummaryRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getPaymentsUsersPaymentsList
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/
 */
export async function getPaymentsUsersPaymentsList(
  user_pk: number, params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string },
  client?: API
): Promise<PaginatedPaymentListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsList(user_pk, params?.currency__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search, params?.status)
  return PaginatedPaymentListListSchema.parse(response)
}

/**
 * createPaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method POST
 * @path /payments/users/{user_pk}/payments/
 */
export async function createPaymentsUsersPayments(
  user_pk: number, data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsCreate(user_pk, data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getPaymentsUsersPaymentsById
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export async function getPaymentsUsersPaymentsById(
  id: string, user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsRetrieve(id, user_pk)
  return PaymentSchema.parse(response)
}

/**
 * updatePaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PUT
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export async function updatePaymentsUsersPayments(
  id: string, user_pk: number, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsUpdate(id, user_pk, data)
  return PaymentSchema.parse(response)
}

/**
 * partialUpdatePaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PATCH
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export async function partialUpdatePaymentsUsersPayments(
  id: string, user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsPartialUpdate(id, user_pk)
  return PaymentSchema.parse(response)
}

/**
 * deletePaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method DELETE
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export async function deletePaymentsUsersPayments(
  id: string, user_pk: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsDestroy(id, user_pk)
  return response
}

/**
 * createPaymentsUsersPaymentsCancel
 *
 * Cancel payment.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/cancel/
 *
 * @method POST
 * @path /payments/users/{user_pk}/payments/{id}/cancel/
 */
export async function createPaymentsUsersPaymentsCancel(
  id: string, user_pk: number, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsCancelCreate(id, user_pk, data)
  return PaymentSchema.parse(response)
}

/**
 * createPaymentsUsersPaymentsCheckStatus
 *
 * Check payment status with provider.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/check_status/
 *
 * @method POST
 * @path /payments/users/{user_pk}/payments/{id}/check_status/
 */
export async function createPaymentsUsersPaymentsCheckStatus(
  id: string, user_pk: number, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsCheckStatusCreate(id, user_pk, data)
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsUsersPaymentsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/health/
 */
export async function getPaymentsUsersPaymentsHealthById(
  user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsHealthRetrieve(user_pk)
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsUsersPaymentsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/stats/
 */
export async function getPaymentsUsersPaymentsStatsById(
  user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsStatsRetrieve(user_pk)
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsUsersPaymentsSummaryById
 *
 * Get user payment summary.
 * 
 * GET /api/v1/users/{user_id}/payments/summary/
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/summary/
 */
export async function getPaymentsUsersPaymentsSummaryById(
  user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersPaymentsSummaryRetrieve(user_pk)
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsUsersSubscriptionsList
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/
 */
export async function getPaymentsUsersSubscriptionsList(
  user_pk: number, params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string },
  client?: API
): Promise<PaginatedSubscriptionListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsList(user_pk, params?.ordering, params?.page, params?.page_size, params?.search, params?.status, params?.tier)
  return PaginatedSubscriptionListListSchema.parse(response)
}

/**
 * createPaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method POST
 * @path /payments/users/{user_pk}/subscriptions/
 */
export async function createPaymentsUsersSubscriptions(
  user_pk: number, data: SubscriptionCreateRequest,
  client?: API
): Promise<SubscriptionCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsCreate(user_pk, data)
  return SubscriptionCreateSchema.parse(response)
}

/**
 * getPaymentsUsersSubscriptionsById
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export async function getPaymentsUsersSubscriptionsById(
  id: string, user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsRetrieve(id, user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * updatePaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method PUT
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export async function updatePaymentsUsersSubscriptions(
  id: string, user_pk: number, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsUpdate(id, user_pk, data)
  return SubscriptionSchema.parse(response)
}

/**
 * partialUpdatePaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method PATCH
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export async function partialUpdatePaymentsUsersSubscriptions(
  id: string, user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsPartialUpdate(id, user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * deletePaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method DELETE
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export async function deletePaymentsUsersSubscriptions(
  id: string, user_pk: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsDestroy(id, user_pk)
  return response
}

/**
 * createPaymentsUsersSubscriptionsIncrementUsage
 *
 * Increment subscription usage.
 * 
 * POST /api/users/{user_id}/subscriptions/{id}/increment_usage/
 *
 * @method POST
 * @path /payments/users/{user_pk}/subscriptions/{id}/increment_usage/
 */
export async function createPaymentsUsersSubscriptionsIncrementUsage(
  id: string, user_pk: number, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsIncrementUsageCreate(id, user_pk, data)
  return SubscriptionSchema.parse(response)
}

/**
 * createPaymentsUsersSubscriptionsUpdateStatus
 *
 * Update subscription status.
 * 
 * POST /api/users/{user_id}/subscriptions/{id}/update_status/
 *
 * @method POST
 * @path /payments/users/{user_pk}/subscriptions/{id}/update_status/
 */
export async function createPaymentsUsersSubscriptionsUpdateStatus(
  id: string, user_pk: number, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsUpdateStatusCreate(id, user_pk, data)
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsUsersSubscriptionsActiveById
 *
 * Get user's active subscription.
 * 
 * GET /api/users/{user_id}/subscriptions/active/
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/active/
 */
export async function getPaymentsUsersSubscriptionsActiveById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsActiveRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsUsersSubscriptionsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/health/
 */
export async function getPaymentsUsersSubscriptionsHealthById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsHealthRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsUsersSubscriptionsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/stats/
 */
export async function getPaymentsUsersSubscriptionsStatsById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsStatsRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsUsersSubscriptionsSummaryById
 *
 * Get user subscription summary.
 * 
 * GET /api/users/{user_id}/subscriptions/summary/
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/summary/
 */
export async function getPaymentsUsersSubscriptionsSummaryById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSubscriptionsSummaryRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getPaymentsUsersHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /payments/users/health/
 */
export async function getPaymentsUsersHealthById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersHealthRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsUsersStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /payments/users/stats/
 */
export async function getPaymentsUsersStatsById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersStatsRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getPaymentsUsersSummaryById
 *
 * Get user payment summary.
 * 
 * GET /api/v1/users/{user_id}/payments/summary/
 *
 * @method GET
 * @path /payments/users/summary/
 */
export async function getPaymentsUsersSummaryById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg_payments.usersSummaryRetrieve()
  return PaymentSchema.parse(response)
}

