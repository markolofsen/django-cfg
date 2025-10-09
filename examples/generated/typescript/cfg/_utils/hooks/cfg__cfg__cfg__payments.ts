/**
 * SWR Hooks for Cfg Payments
 *
 * Auto-generated React hooks for data fetching with SWR.
 *
 * Setup:
 * ```typescript
 * // Configure API once (in your app root)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 * ```
 *
 * Usage:
 * ```typescript
 * // Query hook
 * const { data, error, mutate } = useShopProducts({ page: 1 })
 *
 * // Mutation hook
 * const createProduct = useCreateShopProduct()
 * await createProduct({ name: 'Product', price: 99 })
 * ```
 */
import type { APIKeyCreate } from '../schemas/APIKeyCreate.schema'
import type { APIKeyCreateRequest } from '../schemas/APIKeyCreateRequest.schema'
import type { APIKeyDetail } from '../schemas/APIKeyDetail.schema'
import type { APIKeyUpdate } from '../schemas/APIKeyUpdate.schema'
import type { APIKeyUpdateRequest } from '../schemas/APIKeyUpdateRequest.schema'
import type { APIKeyValidationRequest } from '../schemas/APIKeyValidationRequest.schema'
import type { APIKeyValidationResponse } from '../schemas/APIKeyValidationResponse.schema'
import type { APIKeysOverview } from '../schemas/APIKeysOverview.schema'
import type { AdminPaymentCreate } from '../schemas/AdminPaymentCreate.schema'
import type { AdminPaymentCreateRequest } from '../schemas/AdminPaymentCreateRequest.schema'
import type { AdminPaymentDetail } from '../schemas/AdminPaymentDetail.schema'
import type { AdminPaymentStats } from '../schemas/AdminPaymentStats.schema'
import type { AdminPaymentUpdate } from '../schemas/AdminPaymentUpdate.schema'
import type { AdminPaymentUpdateRequest } from '../schemas/AdminPaymentUpdateRequest.schema'
import type { AdminUser } from '../schemas/AdminUser.schema'
import type { BalanceOverview } from '../schemas/BalanceOverview.schema'
import type { Currency } from '../schemas/Currency.schema'
import type { EndpointGroup } from '../schemas/EndpointGroup.schema'
import type { Network } from '../schemas/Network.schema'
import type { PaginatedAPIKeyListList } from '../schemas/PaginatedAPIKeyListList.schema'
import type { PaginatedAdminPaymentListList } from '../schemas/PaginatedAdminPaymentListList.schema'
import type { PaginatedAdminPaymentStatsList } from '../schemas/PaginatedAdminPaymentStatsList.schema'
import type { PaginatedAdminUserList } from '../schemas/PaginatedAdminUserList.schema'
import type { PaginatedCurrencyListList } from '../schemas/PaginatedCurrencyListList.schema'
import type { PaginatedEndpointGroupList } from '../schemas/PaginatedEndpointGroupList.schema'
import type { PaginatedNetworkList } from '../schemas/PaginatedNetworkList.schema'
import type { PaginatedPaymentListList } from '../schemas/PaginatedPaymentListList.schema'
import type { PaginatedProviderCurrencyList } from '../schemas/PaginatedProviderCurrencyList.schema'
import type { PaginatedRecentPaymentList } from '../schemas/PaginatedRecentPaymentList.schema'
import type { PaginatedRecentTransactionList } from '../schemas/PaginatedRecentTransactionList.schema'
import type { PaginatedSubscriptionListList } from '../schemas/PaginatedSubscriptionListList.schema'
import type { PaginatedTariffList } from '../schemas/PaginatedTariffList.schema'
import type { PaginatedTransactionList } from '../schemas/PaginatedTransactionList.schema'
import type { PaginatedUserBalanceList } from '../schemas/PaginatedUserBalanceList.schema'
import type { PaginatedWebhookEventListList } from '../schemas/PaginatedWebhookEventListList.schema'
import type { PaginatedWebhookStatsList } from '../schemas/PaginatedWebhookStatsList.schema'
import type { PatchedAPIKeyUpdateRequest } from '../schemas/PatchedAPIKeyUpdateRequest.schema'
import type { PatchedAdminPaymentUpdateRequest } from '../schemas/PatchedAdminPaymentUpdateRequest.schema'
import type { PatchedPaymentRequest } from '../schemas/PatchedPaymentRequest.schema'
import type { PatchedSubscriptionRequest } from '../schemas/PatchedSubscriptionRequest.schema'
import type { Payment } from '../schemas/Payment.schema'
import type { PaymentAnalyticsResponse } from '../schemas/PaymentAnalyticsResponse.schema'
import type { PaymentCreate } from '../schemas/PaymentCreate.schema'
import type { PaymentCreateRequest } from '../schemas/PaymentCreateRequest.schema'
import type { PaymentRequest } from '../schemas/PaymentRequest.schema'
import type { PaymentsChartResponse } from '../schemas/PaymentsChartResponse.schema'
import type { PaymentsDashboardOverview } from '../schemas/PaymentsDashboardOverview.schema'
import type { PaymentsMetrics } from '../schemas/PaymentsMetrics.schema'
import type { ProviderCurrency } from '../schemas/ProviderCurrency.schema'
import type { Subscription } from '../schemas/Subscription.schema'
import type { SubscriptionCreate } from '../schemas/SubscriptionCreate.schema'
import type { SubscriptionCreateRequest } from '../schemas/SubscriptionCreateRequest.schema'
import type { SubscriptionOverview } from '../schemas/SubscriptionOverview.schema'
import type { SubscriptionRequest } from '../schemas/SubscriptionRequest.schema'
import type { Tariff } from '../schemas/Tariff.schema'
import type { Transaction } from '../schemas/Transaction.schema'
import type { UserBalance } from '../schemas/UserBalance.schema'
import type { WebhookEventList } from '../schemas/WebhookEventList.schema'
import type { WebhookEventListRequest } from '../schemas/WebhookEventListRequest.schema'
import type { WebhookStats } from '../schemas/WebhookStats.schema'
import type { WebhookStatsRequest } from '../schemas/WebhookStatsRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/payments/
 */
export function useCfgPaymentsAdminApiPaymentsList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number }) {
  return useSWR<PaginatedAdminPaymentListList>(
    params ? ['cfg-payments-admin-api-payments', params] : 'cfg-payments-admin-api-payments',
    () => Fetchers.getCfgPaymentsAdminApiPaymentsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export function useCfgPaymentsAdminApiPaymentsById(id: string) {
  return useSWR<AdminPaymentDetail>(
    ['cfg-payments-admin-api-payment', id],
    () => Fetchers.getCfgPaymentsAdminApiPaymentsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/payments/stats/
 */
export function useCfgPaymentsAdminApiPaymentsStatsById() {
  return useSWR<AdminPaymentStats>(
    'cfg-payments-admin-api-payments-stat',
    () => Fetchers.getCfgPaymentsAdminApiPaymentsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/
 */
export function useCfgPaymentsAdminApiStatsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedAdminPaymentStatsList>(
    params ? ['cfg-payments-admin-api-stats', params] : 'cfg-payments-admin-api-stats',
    () => Fetchers.getCfgPaymentsAdminApiStatsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/{id}/
 */
export function useCfgPaymentsAdminApiStatsById(id: string) {
  return useSWR<AdminPaymentStats>(
    ['cfg-payments-admin-api-stat', id],
    () => Fetchers.getCfgPaymentsAdminApiStatsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/payments/
 */
export function useCfgPaymentsAdminApiStatsPaymentsById() {
  return useSWR<AdminPaymentStats>(
    'cfg-payments-admin-api-stats-payment',
    () => Fetchers.getCfgPaymentsAdminApiStatsPaymentsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/system/
 */
export function useCfgPaymentsAdminApiStatsSystemById() {
  return useSWR<AdminPaymentStats>(
    'cfg-payments-admin-api-stats-system',
    () => Fetchers.getCfgPaymentsAdminApiStatsSystemById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/webhooks/
 */
export function useCfgPaymentsAdminApiStatsWebhooksById() {
  return useSWR<AdminPaymentStats>(
    'cfg-payments-admin-api-stats-webhook',
    () => Fetchers.getCfgPaymentsAdminApiStatsWebhooksById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/users/
 */
export function useCfgPaymentsAdminApiUsersList(params?: { is_active?: boolean; is_staff?: boolean; is_superuser?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedAdminUserList>(
    params ? ['cfg-payments-admin-api-users', params] : 'cfg-payments-admin-api-users',
    () => Fetchers.getCfgPaymentsAdminApiUsersList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/users/{id}/
 */
export function useCfgPaymentsAdminApiUsersById(id: number) {
  return useSWR<AdminUser>(
    ['cfg-payments-admin-api-user', id],
    () => Fetchers.getCfgPaymentsAdminApiUsersById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/
 */
export function useCfgPaymentsAdminApiWebhooksList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedWebhookStatsList>(
    params ? ['cfg-payments-admin-api-webhooks', params] : 'cfg-payments-admin-api-webhooks',
    () => Fetchers.getCfgPaymentsAdminApiWebhooksList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/{id}/
 */
export function useCfgPaymentsAdminApiWebhooksById(id: string) {
  return useSWR<WebhookStats>(
    ['cfg-payments-admin-api-webhook', id],
    () => Fetchers.getCfgPaymentsAdminApiWebhooksById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/
 */
export function useCfgPaymentsAdminApiWebhooksEventsList(webhook_pk: string, params?: { ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedWebhookEventListList>(
    ['cfg-payments-admin-api-webhooks-events', webhook_pk],
    () => Fetchers.getCfgPaymentsAdminApiWebhooksEventsList(webhook_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/{id}/
 */
export function useCfgPaymentsAdminApiWebhooksEventsById(id: string, webhook_pk: string) {
  return useSWR<WebhookEventList>(
    ['cfg-payments-admin-api-webhooks-event', id],
    () => Fetchers.getCfgPaymentsAdminApiWebhooksEventsById(id, webhook_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/stats/
 */
export function useCfgPaymentsAdminApiWebhooksStatsById() {
  return useSWR<WebhookStats>(
    'cfg-payments-admin-api-webhooks-stat',
    () => Fetchers.getCfgPaymentsAdminApiWebhooksStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/api-keys/
 */
export function useCfgPaymentsApiKeysList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; user?: number }) {
  return useSWR<PaginatedAPIKeyListList>(
    params ? ['cfg-payments-api-keys', params] : 'cfg-payments-api-keys',
    () => Fetchers.getCfgPaymentsApiKeysList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/api-keys/{id}/
 */
export function useCfgPaymentsApiKeysById(id: string) {
  return useSWR<APIKeyDetail>(
    ['cfg-payments-api-key', id],
    () => Fetchers.getCfgPaymentsApiKeysById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/api-keys/analytics/
 */
export function useCfgPaymentsApiKeysAnalyticsById() {
  return useSWR<APIKeyDetail>(
    'cfg-payments-api-keys-analytic',
    () => Fetchers.getCfgPaymentsApiKeysAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/api-keys/by_user/
 */
export function useCfgPaymentsApiKeysByUserById() {
  return useSWR<APIKeyDetail>(
    'cfg-payments-api-keys-by-user',
    () => Fetchers.getCfgPaymentsApiKeysByUserById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/api-keys/expiring_soon/
 */
export function useCfgPaymentsApiKeysExpiringSoonById() {
  return useSWR<APIKeyDetail>(
    'cfg-payments-api-keys-expiring-soon',
    () => Fetchers.getCfgPaymentsApiKeysExpiringSoonById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/api-keys/health/
 */
export function useCfgPaymentsApiKeysHealthById() {
  return useSWR<APIKeyDetail>(
    'cfg-payments-api-keys-health',
    () => Fetchers.getCfgPaymentsApiKeysHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/api-keys/stats/
 */
export function useCfgPaymentsApiKeysStatsById() {
  return useSWR<APIKeyDetail>(
    'cfg-payments-api-keys-stat',
    () => Fetchers.getCfgPaymentsApiKeysStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/balances/
 */
export function useCfgPaymentsBalancesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; user?: number }) {
  return useSWR<PaginatedUserBalanceList>(
    params ? ['cfg-payments-balances', params] : 'cfg-payments-balances',
    () => Fetchers.getCfgPaymentsBalancesList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/balances/{id}/
 */
export function useCfgPaymentsBalancesById(id: number) {
  return useSWR<UserBalance>(
    ['cfg-payments-balance', id],
    () => Fetchers.getCfgPaymentsBalancesById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/balances/analytics/
 */
export function useCfgPaymentsBalancesAnalyticsById() {
  return useSWR<UserBalance>(
    'cfg-payments-balances-analytic',
    () => Fetchers.getCfgPaymentsBalancesAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/balances/health/
 */
export function useCfgPaymentsBalancesHealthById() {
  return useSWR<UserBalance>(
    'cfg-payments-balances-health',
    () => Fetchers.getCfgPaymentsBalancesHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/balances/stats/
 */
export function useCfgPaymentsBalancesStatsById() {
  return useSWR<UserBalance>(
    'cfg-payments-balances-stat',
    () => Fetchers.getCfgPaymentsBalancesStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/balances/summary/
 */
export function useCfgPaymentsBalancesSummaryById() {
  return useSWR<UserBalance>(
    'cfg-payments-balances-summary',
    () => Fetchers.getCfgPaymentsBalancesSummaryById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/
 */
export function useCfgPaymentsCurrenciesList(params?: { currency_type?: string; is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedCurrencyListList>(
    params ? ['cfg-payments-currencies', params] : 'cfg-payments-currencies',
    () => Fetchers.getCfgPaymentsCurrenciesList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/{id}/
 */
export function useCfgPaymentsCurrenciesById(id: number) {
  return useSWR<Currency>(
    ['cfg-payments-currencie', id],
    () => Fetchers.getCfgPaymentsCurrenciesById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/{id}/networks/
 */
export function useCfgPaymentsCurrenciesNetworksById(id: number) {
  return useSWR<Currency>(
    ['cfg-payments-currencies-network', id],
    () => Fetchers.getCfgPaymentsCurrenciesNetworksById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/{id}/providers/
 */
export function useCfgPaymentsCurrenciesProvidersById(id: number) {
  return useSWR<Currency>(
    ['cfg-payments-currencies-provider', id],
    () => Fetchers.getCfgPaymentsCurrenciesProvidersById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/crypto/
 */
export function useCfgPaymentsCurrenciesCryptoById() {
  return useSWR<Currency>(
    'cfg-payments-currencies-crypto',
    () => Fetchers.getCfgPaymentsCurrenciesCryptoById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/fiat/
 */
export function useCfgPaymentsCurrenciesFiatById() {
  return useSWR<Currency>(
    'cfg-payments-currencies-fiat',
    () => Fetchers.getCfgPaymentsCurrenciesFiatById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/health/
 */
export function useCfgPaymentsCurrenciesHealthById() {
  return useSWR<Currency>(
    'cfg-payments-currencies-health',
    () => Fetchers.getCfgPaymentsCurrenciesHealthById()
  )
}

/**
 * Get exchange rates
 *
 * @method GET
 * @path /cfg/payments/currencies/rates/
 */
export function useCfgPaymentsCurrenciesRatesById(params: { base_currency: string; currencies: string }) {
  return useSWR<Currency>(
    params ? ['cfg-payments-currencies-rate', params] : 'cfg-payments-currencies-rate',
    () => Fetchers.getCfgPaymentsCurrenciesRatesById(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/stable/
 */
export function useCfgPaymentsCurrenciesStableById() {
  return useSWR<Currency>(
    'cfg-payments-currencies-stable',
    () => Fetchers.getCfgPaymentsCurrenciesStableById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/currencies/stats/
 */
export function useCfgPaymentsCurrenciesStatsById() {
  return useSWR<Currency>(
    'cfg-payments-currencies-stat',
    () => Fetchers.getCfgPaymentsCurrenciesStatsById()
  )
}

/**
 * Get supported currencies
 *
 * @method GET
 * @path /cfg/payments/currencies/supported/
 */
export function useCfgPaymentsCurrenciesSupportedById(params?: { currency_type?: string; provider?: string }) {
  return useSWR<Currency>(
    params ? ['cfg-payments-currencies-supported', params] : 'cfg-payments-currencies-supported',
    () => Fetchers.getCfgPaymentsCurrenciesSupportedById(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/
 */
export function useCfgPaymentsEndpointGroupsList(params?: { is_enabled?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedEndpointGroupList>(
    params ? ['cfg-payments-endpoint-groups', params] : 'cfg-payments-endpoint-groups',
    () => Fetchers.getCfgPaymentsEndpointGroupsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/{id}/
 */
export function useCfgPaymentsEndpointGroupsById(id: number) {
  return useSWR<EndpointGroup>(
    ['cfg-payments-endpoint-group', id],
    () => Fetchers.getCfgPaymentsEndpointGroupsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/available/
 */
export function useCfgPaymentsEndpointGroupsAvailableById() {
  return useSWR<EndpointGroup>(
    'cfg-payments-endpoint-groups-available',
    () => Fetchers.getCfgPaymentsEndpointGroupsAvailableById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/health/
 */
export function useCfgPaymentsEndpointGroupsHealthById() {
  return useSWR<EndpointGroup>(
    'cfg-payments-endpoint-groups-health',
    () => Fetchers.getCfgPaymentsEndpointGroupsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/stats/
 */
export function useCfgPaymentsEndpointGroupsStatsById() {
  return useSWR<EndpointGroup>(
    'cfg-payments-endpoint-groups-stat',
    () => Fetchers.getCfgPaymentsEndpointGroupsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/health/
 */
export function useCfgPaymentsHealthById() {
  return useSWR<Payment>(
    'cfg-payments-health',
    () => Fetchers.getCfgPaymentsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/networks/
 */
export function useCfgPaymentsNetworksList(params?: { is_active?: boolean; native_currency__code?: string; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedNetworkList>(
    params ? ['cfg-payments-networks', params] : 'cfg-payments-networks',
    () => Fetchers.getCfgPaymentsNetworksList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/networks/{id}/
 */
export function useCfgPaymentsNetworksById(id: number) {
  return useSWR<Network>(
    ['cfg-payments-network', id],
    () => Fetchers.getCfgPaymentsNetworksById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/networks/by_currency/
 */
export function useCfgPaymentsNetworksByCurrencyById() {
  return useSWR<Network>(
    'cfg-payments-networks-by-currency',
    () => Fetchers.getCfgPaymentsNetworksByCurrencyById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/networks/health/
 */
export function useCfgPaymentsNetworksHealthById() {
  return useSWR<Network>(
    'cfg-payments-networks-health',
    () => Fetchers.getCfgPaymentsNetworksHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/networks/stats/
 */
export function useCfgPaymentsNetworksStatsById() {
  return useSWR<Network>(
    'cfg-payments-networks-stat',
    () => Fetchers.getCfgPaymentsNetworksStatsById()
  )
}

/**
 * API Keys Overview
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/api_keys_overview/
 */
export function useCfgPaymentsOverviewDashboardApiKeysOverviewById() {
  return useSWR<APIKeysOverview>(
    'cfg-payments-overview-dashboard-api-keys-overview',
    () => Fetchers.getCfgPaymentsOverviewDashboardApiKeysOverviewById()
  )
}

/**
 * Balance Overview
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/balance_overview/
 */
export function useCfgPaymentsOverviewDashboardBalanceOverviewById() {
  return useSWR<BalanceOverview>(
    'cfg-payments-overview-dashboard-balance-overview',
    () => Fetchers.getCfgPaymentsOverviewDashboardBalanceOverviewById()
  )
}

/**
 * Payments Chart Data
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/chart_data/
 */
export function useCfgPaymentsOverviewDashboardChartDataById(params?: { period?: string }) {
  return useSWR<PaymentsChartResponse>(
    params ? ['cfg-payments-overview-dashboard-chart-data', params] : 'cfg-payments-overview-dashboard-chart-data',
    () => Fetchers.getCfgPaymentsOverviewDashboardChartDataById(params)
  )
}

/**
 * Payments Dashboard Metrics
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/metrics/
 */
export function useCfgPaymentsOverviewDashboardMetricsById() {
  return useSWR<PaymentsMetrics>(
    'cfg-payments-overview-dashboard-metric',
    () => Fetchers.getCfgPaymentsOverviewDashboardMetricsById()
  )
}

/**
 * Payments Dashboard Overview
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/overview/
 */
export function useCfgPaymentsOverviewDashboardOverviewById() {
  return useSWR<PaymentsDashboardOverview>(
    'cfg-payments-overview-dashboard-overview',
    () => Fetchers.getCfgPaymentsOverviewDashboardOverviewById()
  )
}

/**
 * Payment Analytics
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/payment_analytics/
 */
export function useCfgPaymentsOverviewDashboardPaymentAnalyticsById(params?: { limit?: number }) {
  return useSWR<PaymentAnalyticsResponse>(
    params ? ['cfg-payments-overview-dashboard-payment-analytic', params] : 'cfg-payments-overview-dashboard-payment-analytic',
    () => Fetchers.getCfgPaymentsOverviewDashboardPaymentAnalyticsById(params)
  )
}

/**
 * Recent Payments
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/recent_payments/
 */
export function useCfgPaymentsOverviewDashboardRecentPaymentsList(params?: { limit?: number; page?: number; page_size?: number }) {
  return useSWR<PaginatedRecentPaymentList>(
    params ? ['cfg-payments-overview-dashboard-recent-payments', params] : 'cfg-payments-overview-dashboard-recent-payments',
    () => Fetchers.getCfgPaymentsOverviewDashboardRecentPaymentsList(params)
  )
}

/**
 * Recent Transactions
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/recent_transactions/
 */
export function useCfgPaymentsOverviewDashboardRecentTransactionsList(params?: { limit?: number; page?: number; page_size?: number }) {
  return useSWR<PaginatedRecentTransactionList>(
    params ? ['cfg-payments-overview-dashboard-recent-transactions', params] : 'cfg-payments-overview-dashboard-recent-transactions',
    () => Fetchers.getCfgPaymentsOverviewDashboardRecentTransactionsList(params)
  )
}

/**
 * Subscription Overview
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/subscription_overview/
 */
export function useCfgPaymentsOverviewDashboardSubscriptionOverviewById() {
  return useSWR<SubscriptionOverview>(
    'cfg-payments-overview-dashboard-subscription-overview',
    () => Fetchers.getCfgPaymentsOverviewDashboardSubscriptionOverviewById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/payments/
 */
export function useCfgPaymentsPaymentsList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number }) {
  return useSWR<PaginatedPaymentListList>(
    params ? ['cfg-payments-payments', params] : 'cfg-payments-payments',
    () => Fetchers.getCfgPaymentsPaymentsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/payments/{id}/
 */
export function useCfgPaymentsPaymentsById(id: string) {
  return useSWR<Payment>(
    ['cfg-payments-payment', id],
    () => Fetchers.getCfgPaymentsPaymentsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/payments/analytics/
 */
export function useCfgPaymentsPaymentsAnalyticsById() {
  return useSWR<Payment>(
    'cfg-payments-payments-analytic',
    () => Fetchers.getCfgPaymentsPaymentsAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/payments/by_provider/
 */
export function useCfgPaymentsPaymentsByProviderById() {
  return useSWR<Payment>(
    'cfg-payments-payments-by-provider',
    () => Fetchers.getCfgPaymentsPaymentsByProviderById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/payments/health/
 */
export function useCfgPaymentsPaymentsHealthById() {
  return useSWR<Payment>(
    'cfg-payments-payments-health',
    () => Fetchers.getCfgPaymentsPaymentsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/payments/stats/
 */
export function useCfgPaymentsPaymentsStatsById() {
  return useSWR<Payment>(
    'cfg-payments-payments-stat',
    () => Fetchers.getCfgPaymentsPaymentsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/payments/status/{id}/
 */
export function useCfgPaymentsPaymentsStatusById(id: string) {
  return useSWR<Payment>(
    ['cfg-payments-payments-statu', id],
    () => Fetchers.getCfgPaymentsPaymentsStatusById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/
 */
export function useCfgPaymentsProviderCurrenciesList(params?: { currency__code?: string; is_enabled?: boolean; network__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string }) {
  return useSWR<PaginatedProviderCurrencyList>(
    params ? ['cfg-payments-provider-currencies', params] : 'cfg-payments-provider-currencies',
    () => Fetchers.getCfgPaymentsProviderCurrenciesList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/{id}/
 */
export function useCfgPaymentsProviderCurrenciesById(id: number) {
  return useSWR<ProviderCurrency>(
    ['cfg-payments-provider-currencie', id],
    () => Fetchers.getCfgPaymentsProviderCurrenciesById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/by_provider/
 */
export function useCfgPaymentsProviderCurrenciesByProviderById() {
  return useSWR<ProviderCurrency>(
    'cfg-payments-provider-currencies-by-provider',
    () => Fetchers.getCfgPaymentsProviderCurrenciesByProviderById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/health/
 */
export function useCfgPaymentsProviderCurrenciesHealthById() {
  return useSWR<ProviderCurrency>(
    'cfg-payments-provider-currencies-health',
    () => Fetchers.getCfgPaymentsProviderCurrenciesHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/limits/
 */
export function useCfgPaymentsProviderCurrenciesLimitsById() {
  return useSWR<ProviderCurrency>(
    'cfg-payments-provider-currencies-limit',
    () => Fetchers.getCfgPaymentsProviderCurrenciesLimitsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/stats/
 */
export function useCfgPaymentsProviderCurrenciesStatsById() {
  return useSWR<ProviderCurrency>(
    'cfg-payments-provider-currencies-stat',
    () => Fetchers.getCfgPaymentsProviderCurrenciesStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/subscriptions/
 */
export function useCfgPaymentsSubscriptionsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string; user?: number }) {
  return useSWR<PaginatedSubscriptionListList>(
    params ? ['cfg-payments-subscriptions', params] : 'cfg-payments-subscriptions',
    () => Fetchers.getCfgPaymentsSubscriptionsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/subscriptions/{id}/
 */
export function useCfgPaymentsSubscriptionsById(id: string) {
  return useSWR<Subscription>(
    ['cfg-payments-subscription', id],
    () => Fetchers.getCfgPaymentsSubscriptionsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/subscriptions/analytics/
 */
export function useCfgPaymentsSubscriptionsAnalyticsById() {
  return useSWR<Subscription>(
    'cfg-payments-subscriptions-analytic',
    () => Fetchers.getCfgPaymentsSubscriptionsAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/subscriptions/by_status/
 */
export function useCfgPaymentsSubscriptionsByStatusById() {
  return useSWR<Subscription>(
    'cfg-payments-subscriptions-by-statu',
    () => Fetchers.getCfgPaymentsSubscriptionsByStatusById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/subscriptions/by_tier/
 */
export function useCfgPaymentsSubscriptionsByTierById() {
  return useSWR<Subscription>(
    'cfg-payments-subscriptions-by-tier',
    () => Fetchers.getCfgPaymentsSubscriptionsByTierById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/subscriptions/health/
 */
export function useCfgPaymentsSubscriptionsHealthById() {
  return useSWR<Subscription>(
    'cfg-payments-subscriptions-health',
    () => Fetchers.getCfgPaymentsSubscriptionsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/subscriptions/stats/
 */
export function useCfgPaymentsSubscriptionsStatsById() {
  return useSWR<Subscription>(
    'cfg-payments-subscriptions-stat',
    () => Fetchers.getCfgPaymentsSubscriptionsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/tariffs/
 */
export function useCfgPaymentsTariffsList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedTariffList>(
    params ? ['cfg-payments-tariffs', params] : 'cfg-payments-tariffs',
    () => Fetchers.getCfgPaymentsTariffsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/tariffs/{id}/
 */
export function useCfgPaymentsTariffsById(id: number) {
  return useSWR<Tariff>(
    ['cfg-payments-tariff', id],
    () => Fetchers.getCfgPaymentsTariffsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/tariffs/{id}/endpoint_groups/
 */
export function useCfgPaymentsTariffsEndpointGroupsById(id: number) {
  return useSWR<Tariff>(
    ['cfg-payments-tariffs-endpoint-group', id],
    () => Fetchers.getCfgPaymentsTariffsEndpointGroupsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/tariffs/free/
 */
export function useCfgPaymentsTariffsFreeById() {
  return useSWR<Tariff>(
    'cfg-payments-tariffs-free',
    () => Fetchers.getCfgPaymentsTariffsFreeById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/tariffs/health/
 */
export function useCfgPaymentsTariffsHealthById() {
  return useSWR<Tariff>(
    'cfg-payments-tariffs-health',
    () => Fetchers.getCfgPaymentsTariffsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/tariffs/paid/
 */
export function useCfgPaymentsTariffsPaidById() {
  return useSWR<Tariff>(
    'cfg-payments-tariffs-paid',
    () => Fetchers.getCfgPaymentsTariffsPaidById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/tariffs/stats/
 */
export function useCfgPaymentsTariffsStatsById() {
  return useSWR<Tariff>(
    'cfg-payments-tariffs-stat',
    () => Fetchers.getCfgPaymentsTariffsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/transactions/
 */
export function useCfgPaymentsTransactionsList(params?: { ordering?: string; page?: number; page_size?: number; payment_id?: string; search?: string; transaction_type?: string; user?: number }) {
  return useSWR<PaginatedTransactionList>(
    params ? ['cfg-payments-transactions', params] : 'cfg-payments-transactions',
    () => Fetchers.getCfgPaymentsTransactionsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/transactions/{id}/
 */
export function useCfgPaymentsTransactionsById(id: string) {
  return useSWR<Transaction>(
    ['cfg-payments-transaction', id],
    () => Fetchers.getCfgPaymentsTransactionsById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/transactions/by_type/
 */
export function useCfgPaymentsTransactionsByTypeById() {
  return useSWR<Transaction>(
    'cfg-payments-transactions-by-type',
    () => Fetchers.getCfgPaymentsTransactionsByTypeById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/transactions/health/
 */
export function useCfgPaymentsTransactionsHealthById() {
  return useSWR<Transaction>(
    'cfg-payments-transactions-health',
    () => Fetchers.getCfgPaymentsTransactionsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/transactions/recent/
 */
export function useCfgPaymentsTransactionsRecentById() {
  return useSWR<Transaction>(
    'cfg-payments-transactions-recent',
    () => Fetchers.getCfgPaymentsTransactionsRecentById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/transactions/stats/
 */
export function useCfgPaymentsTransactionsStatsById() {
  return useSWR<Transaction>(
    'cfg-payments-transactions-stat',
    () => Fetchers.getCfgPaymentsTransactionsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/
 */
export function useCfgPaymentsUsersList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }) {
  return useSWR<PaginatedPaymentListList>(
    params ? ['cfg-payments-users', params] : 'cfg-payments-users',
    () => Fetchers.getCfgPaymentsUsersList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{id}/
 */
export function useCfgPaymentsUsersById(id: string) {
  return useSWR<Payment>(
    ['cfg-payments-user', id],
    () => Fetchers.getCfgPaymentsUsersById(id)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/
 */
export function useCfgPaymentsUsersApiKeysList(user_pk: number, params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedAPIKeyListList>(
    ['cfg-payments-users-api-keys', user_pk],
    () => Fetchers.getCfgPaymentsUsersApiKeysList(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export function useCfgPaymentsUsersApiKeysById(id: string, user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['cfg-payments-users-api-key', id],
    () => Fetchers.getCfgPaymentsUsersApiKeysById(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/active/
 */
export function useCfgPaymentsUsersApiKeysActiveById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['cfg-payments-users-api-keys-active', user_pk],
    () => Fetchers.getCfgPaymentsUsersApiKeysActiveById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/health/
 */
export function useCfgPaymentsUsersApiKeysHealthById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['cfg-payments-users-api-keys-health', user_pk],
    () => Fetchers.getCfgPaymentsUsersApiKeysHealthById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/stats/
 */
export function useCfgPaymentsUsersApiKeysStatsById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['cfg-payments-users-api-keys-stat', user_pk],
    () => Fetchers.getCfgPaymentsUsersApiKeysStatsById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/summary/
 */
export function useCfgPaymentsUsersApiKeysSummaryById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['cfg-payments-users-api-keys-summary', user_pk],
    () => Fetchers.getCfgPaymentsUsersApiKeysSummaryById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/
 */
export function useCfgPaymentsUsersPaymentsList(user_pk: number, params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }) {
  return useSWR<PaginatedPaymentListList>(
    ['cfg-payments-users-payments', user_pk],
    () => Fetchers.getCfgPaymentsUsersPaymentsList(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export function useCfgPaymentsUsersPaymentsById(id: string, user_pk: number) {
  return useSWR<Payment>(
    ['cfg-payments-users-payment', id],
    () => Fetchers.getCfgPaymentsUsersPaymentsById(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/health/
 */
export function useCfgPaymentsUsersPaymentsHealthById(user_pk: number) {
  return useSWR<Payment>(
    ['cfg-payments-users-payments-health', user_pk],
    () => Fetchers.getCfgPaymentsUsersPaymentsHealthById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/stats/
 */
export function useCfgPaymentsUsersPaymentsStatsById(user_pk: number) {
  return useSWR<Payment>(
    ['cfg-payments-users-payments-stat', user_pk],
    () => Fetchers.getCfgPaymentsUsersPaymentsStatsById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/summary/
 */
export function useCfgPaymentsUsersPaymentsSummaryById(user_pk: number) {
  return useSWR<Payment>(
    ['cfg-payments-users-payments-summary', user_pk],
    () => Fetchers.getCfgPaymentsUsersPaymentsSummaryById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/
 */
export function useCfgPaymentsUsersSubscriptionsList(user_pk: number, params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string }) {
  return useSWR<PaginatedSubscriptionListList>(
    ['cfg-payments-users-subscriptions', user_pk],
    () => Fetchers.getCfgPaymentsUsersSubscriptionsList(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export function useCfgPaymentsUsersSubscriptionsById(id: string, user_pk: number) {
  return useSWR<Subscription>(
    ['cfg-payments-users-subscription', id],
    () => Fetchers.getCfgPaymentsUsersSubscriptionsById(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/active/
 */
export function useCfgPaymentsUsersSubscriptionsActiveById(user_pk: number) {
  return useSWR<Subscription>(
    ['cfg-payments-users-subscriptions-active', user_pk],
    () => Fetchers.getCfgPaymentsUsersSubscriptionsActiveById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/health/
 */
export function useCfgPaymentsUsersSubscriptionsHealthById(user_pk: number) {
  return useSWR<Subscription>(
    ['cfg-payments-users-subscriptions-health', user_pk],
    () => Fetchers.getCfgPaymentsUsersSubscriptionsHealthById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/stats/
 */
export function useCfgPaymentsUsersSubscriptionsStatsById(user_pk: number) {
  return useSWR<Subscription>(
    ['cfg-payments-users-subscriptions-stat', user_pk],
    () => Fetchers.getCfgPaymentsUsersSubscriptionsStatsById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/summary/
 */
export function useCfgPaymentsUsersSubscriptionsSummaryById(user_pk: number) {
  return useSWR<Subscription>(
    ['cfg-payments-users-subscriptions-summary', user_pk],
    () => Fetchers.getCfgPaymentsUsersSubscriptionsSummaryById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/health/
 */
export function useCfgPaymentsUsersHealthById() {
  return useSWR<Payment>(
    'cfg-payments-users-health',
    () => Fetchers.getCfgPaymentsUsersHealthById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/stats/
 */
export function useCfgPaymentsUsersStatsById() {
  return useSWR<Payment>(
    'cfg-payments-users-stat',
    () => Fetchers.getCfgPaymentsUsersStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/payments/users/summary/
 */
export function useCfgPaymentsUsersSummaryById() {
  return useSWR<Payment>(
    'cfg-payments-users-summary',
    () => Fetchers.getCfgPaymentsUsersSummaryById()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/
 */
export function useCreateCfgPaymentsAdminApiPayments() {
  const { mutate } = useSWRConfig()

  return async (data: AdminPaymentCreateRequest): Promise<AdminPaymentCreate> => {
    const result = await Fetchers.createCfgPaymentsAdminApiPayments(data)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-payments')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export function useUpdateCfgPaymentsAdminApiPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: AdminPaymentUpdateRequest): Promise<AdminPaymentUpdate> => {
    const result = await Fetchers.updateCfgPaymentsAdminApiPayments(id, data)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-payments')
    mutate('cfg-payments-admin-api-payment')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export function usePartialUpdateCfgPaymentsAdminApiPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<AdminPaymentUpdate> => {
    const result = await Fetchers.partialUpdateCfgPaymentsAdminApiPayments(id)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-payments-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export function useDeleteCfgPaymentsAdminApiPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsAdminApiPayments(id)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-payments')
    mutate('cfg-payments-admin-api-payment')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/{id}/cancel/
 */
export function useCreateCfgPaymentsAdminApiPaymentsCancel() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<AdminPaymentDetail> => {
    const result = await Fetchers.createCfgPaymentsAdminApiPaymentsCancel(id)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-payments-cancel')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/{id}/refresh_status/
 */
export function useCreateCfgPaymentsAdminApiPaymentsRefreshStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<AdminPaymentDetail> => {
    const result = await Fetchers.createCfgPaymentsAdminApiPaymentsRefreshStatus(id)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-payments-refresh-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/{id}/refund/
 */
export function useCreateCfgPaymentsAdminApiPaymentsRefund() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<AdminPaymentDetail> => {
    const result = await Fetchers.createCfgPaymentsAdminApiPaymentsRefund(id)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-payments-refund')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhook-test/test/
 */
export function useCreateCfgPaymentsAdminApiWebhookTestTest() {
  const { mutate } = useSWRConfig()

  return async (data: WebhookStatsRequest): Promise<WebhookStats> => {
    const result = await Fetchers.createCfgPaymentsAdminApiWebhookTestTest(data)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-webhook-test-test')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/{id}/retry/
 */
export function useCreateCfgPaymentsAdminApiWebhooksEventsRetry() {
  const { mutate } = useSWRConfig()

  return async (id: string, webhook_pk: string, data: WebhookEventListRequest): Promise<WebhookEventList> => {
    const result = await Fetchers.createCfgPaymentsAdminApiWebhooksEventsRetry(id, webhook_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-webhooks-events-retry')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/clear_all/
 */
export function useCreateCfgPaymentsAdminApiWebhooksEventsClearAll() {
  const { mutate } = useSWRConfig()

  return async (webhook_pk: string, data: WebhookEventListRequest): Promise<WebhookEventList> => {
    const result = await Fetchers.createCfgPaymentsAdminApiWebhooksEventsClearAll(webhook_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-webhooks-events-clear-all')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/retry_failed/
 */
export function useCreateCfgPaymentsAdminApiWebhooksEventsRetryFailed() {
  const { mutate } = useSWRConfig()

  return async (webhook_pk: string, data: WebhookEventListRequest): Promise<WebhookEventList> => {
    const result = await Fetchers.createCfgPaymentsAdminApiWebhooksEventsRetryFailed(webhook_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-admin-api-webhooks-events-retry-failed')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/api-keys/
 */
export function useCreateCfgPaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyCreateRequest): Promise<APIKeyCreate> => {
    const result = await Fetchers.createCfgPaymentsApiKeys(data)

    // Revalidate related queries
    mutate('cfg-payments-api-keys')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/api-keys/{id}/
 */
export function useUpdateCfgPaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: APIKeyUpdateRequest): Promise<APIKeyUpdate> => {
    const result = await Fetchers.updateCfgPaymentsApiKeys(id, data)

    // Revalidate related queries
    mutate('cfg-payments-api-keys')
    mutate('cfg-payments-api-key')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/api-keys/{id}/
 */
export function usePartialUpdateCfgPaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<APIKeyUpdate> => {
    const result = await Fetchers.partialUpdateCfgPaymentsApiKeys(id)

    // Revalidate related queries
    mutate('cfg-payments-api-keys-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/api-keys/{id}/
 */
export function useDeleteCfgPaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsApiKeys(id)

    // Revalidate related queries
    mutate('cfg-payments-api-keys')
    mutate('cfg-payments-api-key')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/api-keys/{id}/perform_action/
 */
export function useCreateCfgPaymentsApiKeysPerformAction() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<APIKeyDetail> => {
    const result = await Fetchers.createCfgPaymentsApiKeysPerformAction(id)

    // Revalidate related queries
    mutate('cfg-payments-api-keys-perform-action')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/api-keys/create/
 */
export function useCreateCfgPaymentsApiKeysCreate() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyCreateRequest): Promise<APIKeyCreate> => {
    const result = await Fetchers.createCfgPaymentsApiKeysCreate(data)

    // Revalidate related queries
    mutate('cfg-payments-api-keys')

    return result
  }
}

/**
 * Validate API Key (Standalone)
 *
 * @method POST
 * @path /cfg/payments/api-keys/validate/
 */
export function useCreateCfgPaymentsApiKeysValidate() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyValidationRequest): Promise<APIKeyValidationResponse> => {
    const result = await Fetchers.createCfgPaymentsApiKeysValidate(data)

    // Revalidate related queries
    mutate('cfg-payments-api-keys-validate')

    return result
  }
}

/**
 * Validate API Key
 *
 * @method POST
 * @path /cfg/payments/api-keys/validate_key/
 */
export function useCreateCfgPaymentsApiKeysValidateKey() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyValidationRequest): Promise<APIKeyValidationResponse> => {
    const result = await Fetchers.createCfgPaymentsApiKeysValidateKey(data)

    // Revalidate related queries
    mutate('cfg-payments-api-keys-validate-key')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/currencies/
 */
export function useCreateCfgPaymentsCurrencies() {
  const { mutate } = useSWRConfig()

  return async (): Promise<Currency> => {
    const result = await Fetchers.createCfgPaymentsCurrencies()

    // Revalidate related queries
    mutate('cfg-payments-currencies')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/currencies/convert/
 */
export function useCreateCfgPaymentsCurrenciesConvert() {
  const { mutate } = useSWRConfig()

  return async (): Promise<Currency> => {
    const result = await Fetchers.createCfgPaymentsCurrenciesConvert()

    // Revalidate related queries
    mutate('cfg-payments-currencies-convert')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/payments/
 */
export function useCreateCfgPaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createCfgPaymentsPayments(data)

    // Revalidate related queries
    mutate('cfg-payments-payments')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/payments/{id}/
 */
export function useUpdateCfgPaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.updateCfgPaymentsPayments(id, data)

    // Revalidate related queries
    mutate('cfg-payments-payments')
    mutate('cfg-payments-payment')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/payments/{id}/
 */
export function usePartialUpdateCfgPaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<Payment> => {
    const result = await Fetchers.partialUpdateCfgPaymentsPayments(id)

    // Revalidate related queries
    mutate('cfg-payments-payments-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/payments/{id}/
 */
export function useDeleteCfgPaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsPayments(id)

    // Revalidate related queries
    mutate('cfg-payments-payments')
    mutate('cfg-payments-payment')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/payments/{id}/cancel/
 */
export function useCreateCfgPaymentsPaymentsCancel() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createCfgPaymentsPaymentsCancel(id, data)

    // Revalidate related queries
    mutate('cfg-payments-payments-cancel')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/payments/{id}/check_status/
 */
export function useCreateCfgPaymentsPaymentsCheckStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createCfgPaymentsPaymentsCheckStatus(id, data)

    // Revalidate related queries
    mutate('cfg-payments-payments-check-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/payments/create/
 */
export function useCreateCfgPaymentsPaymentsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createCfgPaymentsPaymentsCreate(data)

    // Revalidate related queries
    mutate('cfg-payments-payments')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/subscriptions/
 */
export function useCreateCfgPaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (data: SubscriptionCreateRequest): Promise<SubscriptionCreate> => {
    const result = await Fetchers.createCfgPaymentsSubscriptions(data)

    // Revalidate related queries
    mutate('cfg-payments-subscriptions')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/subscriptions/{id}/
 */
export function useUpdateCfgPaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.updateCfgPaymentsSubscriptions(id, data)

    // Revalidate related queries
    mutate('cfg-payments-subscriptions')
    mutate('cfg-payments-subscription')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/subscriptions/{id}/
 */
export function usePartialUpdateCfgPaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<Subscription> => {
    const result = await Fetchers.partialUpdateCfgPaymentsSubscriptions(id)

    // Revalidate related queries
    mutate('cfg-payments-subscriptions-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/subscriptions/{id}/
 */
export function useDeleteCfgPaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsSubscriptions(id)

    // Revalidate related queries
    mutate('cfg-payments-subscriptions')
    mutate('cfg-payments-subscription')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/subscriptions/{id}/increment_usage/
 */
export function useCreateCfgPaymentsSubscriptionsIncrementUsage() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createCfgPaymentsSubscriptionsIncrementUsage(id, data)

    // Revalidate related queries
    mutate('cfg-payments-subscriptions-increment-usage')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/subscriptions/{id}/update_status/
 */
export function useCreateCfgPaymentsSubscriptionsUpdateStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createCfgPaymentsSubscriptionsUpdateStatus(id, data)

    // Revalidate related queries
    mutate('cfg-payments-subscriptions-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/
 */
export function useCreateCfgPaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createCfgPaymentsUsers(data)

    // Revalidate related queries
    mutate('cfg-payments-users')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/users/{id}/
 */
export function useUpdateCfgPaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.updateCfgPaymentsUsers(id, data)

    // Revalidate related queries
    mutate('cfg-payments-users')
    mutate('cfg-payments-user')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/users/{id}/
 */
export function usePartialUpdateCfgPaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<Payment> => {
    const result = await Fetchers.partialUpdateCfgPaymentsUsers(id)

    // Revalidate related queries
    mutate('cfg-payments-users-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/users/{id}/
 */
export function useDeleteCfgPaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsUsers(id)

    // Revalidate related queries
    mutate('cfg-payments-users')
    mutate('cfg-payments-user')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{id}/cancel/
 */
export function useCreateCfgPaymentsUsersCancel() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createCfgPaymentsUsersCancel(id, data)

    // Revalidate related queries
    mutate('cfg-payments-users-cancel')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{id}/check_status/
 */
export function useCreateCfgPaymentsUsersCheckStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createCfgPaymentsUsersCheckStatus(id, data)

    // Revalidate related queries
    mutate('cfg-payments-users-check-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/api-keys/
 */
export function useCreateCfgPaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (user_pk: number, data: APIKeyCreateRequest): Promise<APIKeyCreate> => {
    const result = await Fetchers.createCfgPaymentsUsersApiKeys(user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-api-keys')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export function useUpdateCfgPaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: APIKeyUpdateRequest): Promise<APIKeyUpdate> => {
    const result = await Fetchers.updateCfgPaymentsUsersApiKeys(id, user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-api-keys')
    mutate('cfg-payments-users-api-key')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export function usePartialUpdateCfgPaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<APIKeyUpdate> => {
    const result = await Fetchers.partialUpdateCfgPaymentsUsersApiKeys(id, user_pk)

    // Revalidate related queries
    mutate('cfg-payments-users-api-keys-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export function useDeleteCfgPaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsUsersApiKeys(id, user_pk)

    // Revalidate related queries
    mutate('cfg-payments-users-api-keys')
    mutate('cfg-payments-users-api-key')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/perform_action/
 */
export function useCreateCfgPaymentsUsersApiKeysPerformAction() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<APIKeyDetail> => {
    const result = await Fetchers.createCfgPaymentsUsersApiKeysPerformAction(id, user_pk)

    // Revalidate related queries
    mutate('cfg-payments-users-api-keys-perform-action')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/payments/
 */
export function useCreateCfgPaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (user_pk: number, data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createCfgPaymentsUsersPayments(user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-payments')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export function useUpdateCfgPaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.updateCfgPaymentsUsersPayments(id, user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-payments')
    mutate('cfg-payments-users-payment')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export function usePartialUpdateCfgPaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<Payment> => {
    const result = await Fetchers.partialUpdateCfgPaymentsUsersPayments(id, user_pk)

    // Revalidate related queries
    mutate('cfg-payments-users-payments-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export function useDeleteCfgPaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsUsersPayments(id, user_pk)

    // Revalidate related queries
    mutate('cfg-payments-users-payments')
    mutate('cfg-payments-users-payment')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/payments/{id}/cancel/
 */
export function useCreateCfgPaymentsUsersPaymentsCancel() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createCfgPaymentsUsersPaymentsCancel(id, user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-payments-cancel')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/payments/{id}/check_status/
 */
export function useCreateCfgPaymentsUsersPaymentsCheckStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createCfgPaymentsUsersPaymentsCheckStatus(id, user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-payments-check-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/subscriptions/
 */
export function useCreateCfgPaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (user_pk: number, data: SubscriptionCreateRequest): Promise<SubscriptionCreate> => {
    const result = await Fetchers.createCfgPaymentsUsersSubscriptions(user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-subscriptions')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export function useUpdateCfgPaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.updateCfgPaymentsUsersSubscriptions(id, user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-subscriptions')
    mutate('cfg-payments-users-subscription')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export function usePartialUpdateCfgPaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<Subscription> => {
    const result = await Fetchers.partialUpdateCfgPaymentsUsersSubscriptions(id, user_pk)

    // Revalidate related queries
    mutate('cfg-payments-users-subscriptions-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export function useDeleteCfgPaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<void> => {
    const result = await Fetchers.deleteCfgPaymentsUsersSubscriptions(id, user_pk)

    // Revalidate related queries
    mutate('cfg-payments-users-subscriptions')
    mutate('cfg-payments-users-subscription')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/increment_usage/
 */
export function useCreateCfgPaymentsUsersSubscriptionsIncrementUsage() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createCfgPaymentsUsersSubscriptionsIncrementUsage(id, user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-subscriptions-increment-usage')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/update_status/
 */
export function useCreateCfgPaymentsUsersSubscriptionsUpdateStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createCfgPaymentsUsersSubscriptionsUpdateStatus(id, user_pk, data)

    // Revalidate related queries
    mutate('cfg-payments-users-subscriptions-status')

    return result
  }
}
