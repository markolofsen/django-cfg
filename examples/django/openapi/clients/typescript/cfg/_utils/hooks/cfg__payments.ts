/**
 * SWR Hooks for Payments
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
import type { BalanceOverview } from '../schemas/BalanceOverview.schema'
import type { Currency } from '../schemas/Currency.schema'
import type { EndpointGroup } from '../schemas/EndpointGroup.schema'
import type { Network } from '../schemas/Network.schema'
import type { PaginatedAPIKeyListList } from '../schemas/PaginatedAPIKeyListList.schema'
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
import type { PatchedAPIKeyUpdateRequest } from '../schemas/PatchedAPIKeyUpdateRequest.schema'
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
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 *
 * @method GET
 * @path /payments/api-keys/
 */
export function usePaymentsApiKeysList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; user?: number }) {
  return useSWR<PaginatedAPIKeyListList>(
    params ? ['payments-api-keys', params] : 'payments-api-keys',
    () => Fetchers.getPaymentsApiKeysList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/{id}/
 */
export function usePaymentsApiKeysById(id: string) {
  return useSWR<APIKeyDetail>(
    ['payments-api-key', id],
    () => Fetchers.getPaymentsApiKeysById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/analytics/
 */
export function usePaymentsApiKeysAnalyticsById() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-analytic',
    () => Fetchers.getPaymentsApiKeysAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/by_user/
 */
export function usePaymentsApiKeysByUserById() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-by-user',
    () => Fetchers.getPaymentsApiKeysByUserById()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/expiring_soon/
 */
export function usePaymentsApiKeysExpiringSoonById() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-expiring-soon',
    () => Fetchers.getPaymentsApiKeysExpiringSoonById()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/health/
 */
export function usePaymentsApiKeysHealthById() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-health',
    () => Fetchers.getPaymentsApiKeysHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/stats/
 */
export function usePaymentsApiKeysStatsById() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-stat',
    () => Fetchers.getPaymentsApiKeysStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/
 */
export function usePaymentsBalancesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; user?: number }) {
  return useSWR<PaginatedUserBalanceList>(
    params ? ['payments-balances', params] : 'payments-balances',
    () => Fetchers.getPaymentsBalancesList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/{id}/
 */
export function usePaymentsBalancesById(id: number) {
  return useSWR<UserBalance>(
    ['payments-balance', id],
    () => Fetchers.getPaymentsBalancesById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/analytics/
 */
export function usePaymentsBalancesAnalyticsById() {
  return useSWR<UserBalance>(
    'payments-balances-analytic',
    () => Fetchers.getPaymentsBalancesAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/health/
 */
export function usePaymentsBalancesHealthById() {
  return useSWR<UserBalance>(
    'payments-balances-health',
    () => Fetchers.getPaymentsBalancesHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/stats/
 */
export function usePaymentsBalancesStatsById() {
  return useSWR<UserBalance>(
    'payments-balances-stat',
    () => Fetchers.getPaymentsBalancesStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/summary/
 */
export function usePaymentsBalancesSummaryById() {
  return useSWR<UserBalance>(
    'payments-balances-summary',
    () => Fetchers.getPaymentsBalancesSummaryById()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/
 */
export function usePaymentsCurrenciesList(params?: { currency_type?: string; is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedCurrencyListList>(
    params ? ['payments-currencies', params] : 'payments-currencies',
    () => Fetchers.getPaymentsCurrenciesList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/{id}/
 */
export function usePaymentsCurrenciesById(id: number) {
  return useSWR<Currency>(
    ['payments-currencie', id],
    () => Fetchers.getPaymentsCurrenciesById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/{id}/networks/
 */
export function usePaymentsCurrenciesNetworksById(id: number) {
  return useSWR<Currency>(
    ['payments-currencies-network', id],
    () => Fetchers.getPaymentsCurrenciesNetworksById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/{id}/providers/
 */
export function usePaymentsCurrenciesProvidersById(id: number) {
  return useSWR<Currency>(
    ['payments-currencies-provider', id],
    () => Fetchers.getPaymentsCurrenciesProvidersById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/crypto/
 */
export function usePaymentsCurrenciesCryptoById() {
  return useSWR<Currency>(
    'payments-currencies-crypto',
    () => Fetchers.getPaymentsCurrenciesCryptoById()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/fiat/
 */
export function usePaymentsCurrenciesFiatById() {
  return useSWR<Currency>(
    'payments-currencies-fiat',
    () => Fetchers.getPaymentsCurrenciesFiatById()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/health/
 */
export function usePaymentsCurrenciesHealthById() {
  return useSWR<Currency>(
    'payments-currencies-health',
    () => Fetchers.getPaymentsCurrenciesHealthById()
  )
}

/**
 * Get exchange rates
 *
 * @method GET
 * @path /payments/currencies/rates/
 */
export function usePaymentsCurrenciesRatesById(params: { base_currency: string; currencies: string }) {
  return useSWR<Currency>(
    params ? ['payments-currencies-rate', params] : 'payments-currencies-rate',
    () => Fetchers.getPaymentsCurrenciesRatesById(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/stable/
 */
export function usePaymentsCurrenciesStableById() {
  return useSWR<Currency>(
    'payments-currencies-stable',
    () => Fetchers.getPaymentsCurrenciesStableById()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/stats/
 */
export function usePaymentsCurrenciesStatsById() {
  return useSWR<Currency>(
    'payments-currencies-stat',
    () => Fetchers.getPaymentsCurrenciesStatsById()
  )
}

/**
 * Get supported currencies
 *
 * @method GET
 * @path /payments/currencies/supported/
 */
export function usePaymentsCurrenciesSupportedById(params?: { currency_type?: string; provider?: string }) {
  return useSWR<Currency>(
    params ? ['payments-currencies-supported', params] : 'payments-currencies-supported',
    () => Fetchers.getPaymentsCurrenciesSupportedById(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/
 */
export function usePaymentsEndpointGroupsList(params?: { is_enabled?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedEndpointGroupList>(
    params ? ['payments-endpoint-groups', params] : 'payments-endpoint-groups',
    () => Fetchers.getPaymentsEndpointGroupsList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/{id}/
 */
export function usePaymentsEndpointGroupsById(id: number) {
  return useSWR<EndpointGroup>(
    ['payments-endpoint-group', id],
    () => Fetchers.getPaymentsEndpointGroupsById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/available/
 */
export function usePaymentsEndpointGroupsAvailableById() {
  return useSWR<EndpointGroup>(
    'payments-endpoint-groups-available',
    () => Fetchers.getPaymentsEndpointGroupsAvailableById()
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/health/
 */
export function usePaymentsEndpointGroupsHealthById() {
  return useSWR<EndpointGroup>(
    'payments-endpoint-groups-health',
    () => Fetchers.getPaymentsEndpointGroupsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/stats/
 */
export function usePaymentsEndpointGroupsStatsById() {
  return useSWR<EndpointGroup>(
    'payments-endpoint-groups-stat',
    () => Fetchers.getPaymentsEndpointGroupsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/health/
 */
export function usePaymentsHealthById() {
  return useSWR<Payment>(
    'payments-health',
    () => Fetchers.getPaymentsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/
 */
export function usePaymentsNetworksList(params?: { is_active?: boolean; native_currency__code?: string; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedNetworkList>(
    params ? ['payments-networks', params] : 'payments-networks',
    () => Fetchers.getPaymentsNetworksList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/{id}/
 */
export function usePaymentsNetworksById(id: number) {
  return useSWR<Network>(
    ['payments-network', id],
    () => Fetchers.getPaymentsNetworksById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/by_currency/
 */
export function usePaymentsNetworksByCurrencyById() {
  return useSWR<Network>(
    'payments-networks-by-currency',
    () => Fetchers.getPaymentsNetworksByCurrencyById()
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/health/
 */
export function usePaymentsNetworksHealthById() {
  return useSWR<Network>(
    'payments-networks-health',
    () => Fetchers.getPaymentsNetworksHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/stats/
 */
export function usePaymentsNetworksStatsById() {
  return useSWR<Network>(
    'payments-networks-stat',
    () => Fetchers.getPaymentsNetworksStatsById()
  )
}

/**
 * API Keys Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/api_keys_overview/
 */
export function usePaymentsOverviewDashboardApiKeysOverviewById() {
  return useSWR<APIKeysOverview>(
    'payments-overview-dashboard-api-keys-overview',
    () => Fetchers.getPaymentsOverviewDashboardApiKeysOverviewById()
  )
}

/**
 * Balance Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/balance_overview/
 */
export function usePaymentsOverviewDashboardBalanceOverviewById() {
  return useSWR<BalanceOverview>(
    'payments-overview-dashboard-balance-overview',
    () => Fetchers.getPaymentsOverviewDashboardBalanceOverviewById()
  )
}

/**
 * Payments Chart Data
 *
 * @method GET
 * @path /payments/overview/dashboard/chart_data/
 */
export function usePaymentsOverviewDashboardChartDataById(params?: { period?: string }) {
  return useSWR<PaymentsChartResponse>(
    params ? ['payments-overview-dashboard-chart-data', params] : 'payments-overview-dashboard-chart-data',
    () => Fetchers.getPaymentsOverviewDashboardChartDataById(params)
  )
}

/**
 * Payments Dashboard Metrics
 *
 * @method GET
 * @path /payments/overview/dashboard/metrics/
 */
export function usePaymentsOverviewDashboardMetricsById() {
  return useSWR<PaymentsMetrics>(
    'payments-overview-dashboard-metric',
    () => Fetchers.getPaymentsOverviewDashboardMetricsById()
  )
}

/**
 * Payments Dashboard Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/overview/
 */
export function usePaymentsOverviewDashboardOverviewById() {
  return useSWR<PaymentsDashboardOverview>(
    'payments-overview-dashboard-overview',
    () => Fetchers.getPaymentsOverviewDashboardOverviewById()
  )
}

/**
 * Payment Analytics
 *
 * @method GET
 * @path /payments/overview/dashboard/payment_analytics/
 */
export function usePaymentsOverviewDashboardPaymentAnalyticsById(params?: { limit?: number }) {
  return useSWR<PaymentAnalyticsResponse>(
    params ? ['payments-overview-dashboard-payment-analytic', params] : 'payments-overview-dashboard-payment-analytic',
    () => Fetchers.getPaymentsOverviewDashboardPaymentAnalyticsById(params)
  )
}

/**
 * Recent Payments
 *
 * @method GET
 * @path /payments/overview/dashboard/recent_payments/
 */
export function usePaymentsOverviewDashboardRecentPaymentsList(params?: { limit?: number; page?: number; page_size?: number }) {
  return useSWR<PaginatedRecentPaymentList>(
    params ? ['payments-overview-dashboard-recent-payments', params] : 'payments-overview-dashboard-recent-payments',
    () => Fetchers.getPaymentsOverviewDashboardRecentPaymentsList(params)
  )
}

/**
 * Recent Transactions
 *
 * @method GET
 * @path /payments/overview/dashboard/recent_transactions/
 */
export function usePaymentsOverviewDashboardRecentTransactionsList(params?: { limit?: number; page?: number; page_size?: number }) {
  return useSWR<PaginatedRecentTransactionList>(
    params ? ['payments-overview-dashboard-recent-transactions', params] : 'payments-overview-dashboard-recent-transactions',
    () => Fetchers.getPaymentsOverviewDashboardRecentTransactionsList(params)
  )
}

/**
 * Subscription Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/subscription_overview/
 */
export function usePaymentsOverviewDashboardSubscriptionOverviewById() {
  return useSWR<SubscriptionOverview>(
    'payments-overview-dashboard-subscription-overview',
    () => Fetchers.getPaymentsOverviewDashboardSubscriptionOverviewById()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/
 */
export function usePaymentsPaymentsList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number }) {
  return useSWR<PaginatedPaymentListList>(
    params ? ['payments-payments', params] : 'payments-payments',
    () => Fetchers.getPaymentsPaymentsList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/{id}/
 */
export function usePaymentsPaymentsById(id: string) {
  return useSWR<Payment>(
    ['payments-payment', id],
    () => Fetchers.getPaymentsPaymentsById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/analytics/
 */
export function usePaymentsPaymentsAnalyticsById() {
  return useSWR<Payment>(
    'payments-payments-analytic',
    () => Fetchers.getPaymentsPaymentsAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/by_provider/
 */
export function usePaymentsPaymentsByProviderById() {
  return useSWR<Payment>(
    'payments-payments-by-provider',
    () => Fetchers.getPaymentsPaymentsByProviderById()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/health/
 */
export function usePaymentsPaymentsHealthById() {
  return useSWR<Payment>(
    'payments-payments-health',
    () => Fetchers.getPaymentsPaymentsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/stats/
 */
export function usePaymentsPaymentsStatsById() {
  return useSWR<Payment>(
    'payments-payments-stat',
    () => Fetchers.getPaymentsPaymentsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/status/{id}/
 */
export function usePaymentsPaymentsStatusById(id: string) {
  return useSWR<Payment>(
    ['payments-payments-statu', id],
    () => Fetchers.getPaymentsPaymentsStatusById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/
 */
export function usePaymentsProviderCurrenciesList(params?: { currency__code?: string; is_enabled?: boolean; network__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string }) {
  return useSWR<PaginatedProviderCurrencyList>(
    params ? ['payments-provider-currencies', params] : 'payments-provider-currencies',
    () => Fetchers.getPaymentsProviderCurrenciesList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/{id}/
 */
export function usePaymentsProviderCurrenciesById(id: number) {
  return useSWR<ProviderCurrency>(
    ['payments-provider-currencie', id],
    () => Fetchers.getPaymentsProviderCurrenciesById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/by_provider/
 */
export function usePaymentsProviderCurrenciesByProviderById() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-by-provider',
    () => Fetchers.getPaymentsProviderCurrenciesByProviderById()
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/health/
 */
export function usePaymentsProviderCurrenciesHealthById() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-health',
    () => Fetchers.getPaymentsProviderCurrenciesHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/limits/
 */
export function usePaymentsProviderCurrenciesLimitsById() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-limit',
    () => Fetchers.getPaymentsProviderCurrenciesLimitsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/stats/
 */
export function usePaymentsProviderCurrenciesStatsById() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-stat',
    () => Fetchers.getPaymentsProviderCurrenciesStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/
 */
export function usePaymentsSubscriptionsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string; user?: number }) {
  return useSWR<PaginatedSubscriptionListList>(
    params ? ['payments-subscriptions', params] : 'payments-subscriptions',
    () => Fetchers.getPaymentsSubscriptionsList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/{id}/
 */
export function usePaymentsSubscriptionsById(id: string) {
  return useSWR<Subscription>(
    ['payments-subscription', id],
    () => Fetchers.getPaymentsSubscriptionsById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/analytics/
 */
export function usePaymentsSubscriptionsAnalyticsById() {
  return useSWR<Subscription>(
    'payments-subscriptions-analytic',
    () => Fetchers.getPaymentsSubscriptionsAnalyticsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/by_status/
 */
export function usePaymentsSubscriptionsByStatusById() {
  return useSWR<Subscription>(
    'payments-subscriptions-by-statu',
    () => Fetchers.getPaymentsSubscriptionsByStatusById()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/by_tier/
 */
export function usePaymentsSubscriptionsByTierById() {
  return useSWR<Subscription>(
    'payments-subscriptions-by-tier',
    () => Fetchers.getPaymentsSubscriptionsByTierById()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/health/
 */
export function usePaymentsSubscriptionsHealthById() {
  return useSWR<Subscription>(
    'payments-subscriptions-health',
    () => Fetchers.getPaymentsSubscriptionsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/stats/
 */
export function usePaymentsSubscriptionsStatsById() {
  return useSWR<Subscription>(
    'payments-subscriptions-stat',
    () => Fetchers.getPaymentsSubscriptionsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/
 */
export function usePaymentsTariffsList(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedTariffList>(
    params ? ['payments-tariffs', params] : 'payments-tariffs',
    () => Fetchers.getPaymentsTariffsList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/{id}/
 */
export function usePaymentsTariffsById(id: number) {
  return useSWR<Tariff>(
    ['payments-tariff', id],
    () => Fetchers.getPaymentsTariffsById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/{id}/endpoint_groups/
 */
export function usePaymentsTariffsEndpointGroupsById(id: number) {
  return useSWR<Tariff>(
    ['payments-tariffs-endpoint-group', id],
    () => Fetchers.getPaymentsTariffsEndpointGroupsById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/free/
 */
export function usePaymentsTariffsFreeById() {
  return useSWR<Tariff>(
    'payments-tariffs-free',
    () => Fetchers.getPaymentsTariffsFreeById()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/health/
 */
export function usePaymentsTariffsHealthById() {
  return useSWR<Tariff>(
    'payments-tariffs-health',
    () => Fetchers.getPaymentsTariffsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/paid/
 */
export function usePaymentsTariffsPaidById() {
  return useSWR<Tariff>(
    'payments-tariffs-paid',
    () => Fetchers.getPaymentsTariffsPaidById()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/stats/
 */
export function usePaymentsTariffsStatsById() {
  return useSWR<Tariff>(
    'payments-tariffs-stat',
    () => Fetchers.getPaymentsTariffsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/
 */
export function usePaymentsTransactionsList(params?: { ordering?: string; page?: number; page_size?: number; payment_id?: string; search?: string; transaction_type?: string; user?: number }) {
  return useSWR<PaginatedTransactionList>(
    params ? ['payments-transactions', params] : 'payments-transactions',
    () => Fetchers.getPaymentsTransactionsList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/{id}/
 */
export function usePaymentsTransactionsById(id: string) {
  return useSWR<Transaction>(
    ['payments-transaction', id],
    () => Fetchers.getPaymentsTransactionsById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/by_type/
 */
export function usePaymentsTransactionsByTypeById() {
  return useSWR<Transaction>(
    'payments-transactions-by-type',
    () => Fetchers.getPaymentsTransactionsByTypeById()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/health/
 */
export function usePaymentsTransactionsHealthById() {
  return useSWR<Transaction>(
    'payments-transactions-health',
    () => Fetchers.getPaymentsTransactionsHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/recent/
 */
export function usePaymentsTransactionsRecentById() {
  return useSWR<Transaction>(
    'payments-transactions-recent',
    () => Fetchers.getPaymentsTransactionsRecentById()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/stats/
 */
export function usePaymentsTransactionsStatsById() {
  return useSWR<Transaction>(
    'payments-transactions-stat',
    () => Fetchers.getPaymentsTransactionsStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/users/
 */
export function usePaymentsUsersList(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }) {
  return useSWR<PaginatedPaymentListList>(
    params ? ['payments-users', params] : 'payments-users',
    () => Fetchers.getPaymentsUsersList(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{id}/
 */
export function usePaymentsUsersById(id: string) {
  return useSWR<Payment>(
    ['payments-user', id],
    () => Fetchers.getPaymentsUsersById(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/
 */
export function usePaymentsUsersApiKeysList(user_pk: number, params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedAPIKeyListList>(
    ['payments-users-api-keys', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysList(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export function usePaymentsUsersApiKeysById(id: string, user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-key', id],
    () => Fetchers.getPaymentsUsersApiKeysById(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/active/
 */
export function usePaymentsUsersApiKeysActiveById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-active', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysActiveById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/health/
 */
export function usePaymentsUsersApiKeysHealthById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-health', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysHealthById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/stats/
 */
export function usePaymentsUsersApiKeysStatsById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-stat', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysStatsById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/summary/
 */
export function usePaymentsUsersApiKeysSummaryById(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-summary', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysSummaryById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/
 */
export function usePaymentsUsersPaymentsList(user_pk: number, params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }) {
  return useSWR<PaginatedPaymentListList>(
    ['payments-users-payments', user_pk],
    () => Fetchers.getPaymentsUsersPaymentsList(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export function usePaymentsUsersPaymentsById(id: string, user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payment', id],
    () => Fetchers.getPaymentsUsersPaymentsById(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/health/
 */
export function usePaymentsUsersPaymentsHealthById(user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payments-health', user_pk],
    () => Fetchers.getPaymentsUsersPaymentsHealthById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/stats/
 */
export function usePaymentsUsersPaymentsStatsById(user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payments-stat', user_pk],
    () => Fetchers.getPaymentsUsersPaymentsStatsById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/summary/
 */
export function usePaymentsUsersPaymentsSummaryById(user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payments-summary', user_pk],
    () => Fetchers.getPaymentsUsersPaymentsSummaryById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/
 */
export function usePaymentsUsersSubscriptionsList(user_pk: number, params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string }) {
  return useSWR<PaginatedSubscriptionListList>(
    ['payments-users-subscriptions', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsList(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export function usePaymentsUsersSubscriptionsById(id: string, user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscription', id],
    () => Fetchers.getPaymentsUsersSubscriptionsById(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/active/
 */
export function usePaymentsUsersSubscriptionsActiveById(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-active', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsActiveById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/health/
 */
export function usePaymentsUsersSubscriptionsHealthById(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-health', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsHealthById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/stats/
 */
export function usePaymentsUsersSubscriptionsStatsById(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-stat', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsStatsById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/summary/
 */
export function usePaymentsUsersSubscriptionsSummaryById(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-summary', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsSummaryById(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/health/
 */
export function usePaymentsUsersHealthById() {
  return useSWR<Payment>(
    'payments-users-health',
    () => Fetchers.getPaymentsUsersHealthById()
  )
}

/**
 *
 * @method GET
 * @path /payments/users/stats/
 */
export function usePaymentsUsersStatsById() {
  return useSWR<Payment>(
    'payments-users-stat',
    () => Fetchers.getPaymentsUsersStatsById()
  )
}

/**
 *
 * @method GET
 * @path /payments/users/summary/
 */
export function usePaymentsUsersSummaryById() {
  return useSWR<Payment>(
    'payments-users-summary',
    () => Fetchers.getPaymentsUsersSummaryById()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /payments/api-keys/
 */
export function useCreatePaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyCreateRequest): Promise<APIKeyCreate> => {
    const result = await Fetchers.createPaymentsApiKeys(data)

    // Revalidate related queries
    mutate('payments-api-keys')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /payments/api-keys/{id}/
 */
export function useUpdatePaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: APIKeyUpdateRequest): Promise<APIKeyUpdate> => {
    const result = await Fetchers.updatePaymentsApiKeys(id, data)

    // Revalidate related queries
    mutate('payments-api-keys')
    mutate('payments-api-key')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /payments/api-keys/{id}/
 */
export function usePartialUpdatePaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<APIKeyUpdate> => {
    const result = await Fetchers.partialUpdatePaymentsApiKeys(id)

    // Revalidate related queries
    mutate('payments-api-keys-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /payments/api-keys/{id}/
 */
export function useDeletePaymentsApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deletePaymentsApiKeys(id)

    // Revalidate related queries
    mutate('payments-api-keys')
    mutate('payments-api-key')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/api-keys/{id}/perform_action/
 */
export function useCreatePaymentsApiKeysPerformAction() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<APIKeyDetail> => {
    const result = await Fetchers.createPaymentsApiKeysPerformAction(id)

    // Revalidate related queries
    mutate('payments-api-keys-perform-action')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/api-keys/create/
 */
export function useCreatePaymentsApiKeysCreate() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyCreateRequest): Promise<APIKeyCreate> => {
    const result = await Fetchers.createPaymentsApiKeysCreate(data)

    // Revalidate related queries
    mutate('payments-api-keys')

    return result
  }
}

/**
 * Validate API Key (Standalone)
 *
 * @method POST
 * @path /payments/api-keys/validate/
 */
export function useCreatePaymentsApiKeysValidate() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyValidationRequest): Promise<APIKeyValidationResponse> => {
    const result = await Fetchers.createPaymentsApiKeysValidate(data)

    // Revalidate related queries
    mutate('payments-api-keys-validate')

    return result
  }
}

/**
 * Validate API Key
 *
 * @method POST
 * @path /payments/api-keys/validate_key/
 */
export function useCreatePaymentsApiKeysValidateKey() {
  const { mutate } = useSWRConfig()

  return async (data: APIKeyValidationRequest): Promise<APIKeyValidationResponse> => {
    const result = await Fetchers.createPaymentsApiKeysValidateKey(data)

    // Revalidate related queries
    mutate('payments-api-keys-validate-key')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/currencies/
 */
export function useCreatePaymentsCurrencies() {
  const { mutate } = useSWRConfig()

  return async (): Promise<Currency> => {
    const result = await Fetchers.createPaymentsCurrencies()

    // Revalidate related queries
    mutate('payments-currencies')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/currencies/convert/
 */
export function useCreatePaymentsCurrenciesConvert() {
  const { mutate } = useSWRConfig()

  return async (): Promise<Currency> => {
    const result = await Fetchers.createPaymentsCurrenciesConvert()

    // Revalidate related queries
    mutate('payments-currencies-convert')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/payments/
 */
export function useCreatePaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createPaymentsPayments(data)

    // Revalidate related queries
    mutate('payments-payments')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /payments/payments/{id}/
 */
export function useUpdatePaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.updatePaymentsPayments(id, data)

    // Revalidate related queries
    mutate('payments-payments')
    mutate('payments-payment')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /payments/payments/{id}/
 */
export function usePartialUpdatePaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<Payment> => {
    const result = await Fetchers.partialUpdatePaymentsPayments(id)

    // Revalidate related queries
    mutate('payments-payments-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /payments/payments/{id}/
 */
export function useDeletePaymentsPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deletePaymentsPayments(id)

    // Revalidate related queries
    mutate('payments-payments')
    mutate('payments-payment')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/payments/{id}/cancel/
 */
export function useCreatePaymentsPaymentsCancel() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createPaymentsPaymentsCancel(id, data)

    // Revalidate related queries
    mutate('payments-payments-cancel')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/payments/{id}/check_status/
 */
export function useCreatePaymentsPaymentsCheckStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createPaymentsPaymentsCheckStatus(id, data)

    // Revalidate related queries
    mutate('payments-payments-check-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/payments/create/
 */
export function useCreatePaymentsPaymentsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createPaymentsPaymentsCreate(data)

    // Revalidate related queries
    mutate('payments-payments')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/subscriptions/
 */
export function useCreatePaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (data: SubscriptionCreateRequest): Promise<SubscriptionCreate> => {
    const result = await Fetchers.createPaymentsSubscriptions(data)

    // Revalidate related queries
    mutate('payments-subscriptions')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /payments/subscriptions/{id}/
 */
export function useUpdatePaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.updatePaymentsSubscriptions(id, data)

    // Revalidate related queries
    mutate('payments-subscriptions')
    mutate('payments-subscription')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /payments/subscriptions/{id}/
 */
export function usePartialUpdatePaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<Subscription> => {
    const result = await Fetchers.partialUpdatePaymentsSubscriptions(id)

    // Revalidate related queries
    mutate('payments-subscriptions-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /payments/subscriptions/{id}/
 */
export function useDeletePaymentsSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deletePaymentsSubscriptions(id)

    // Revalidate related queries
    mutate('payments-subscriptions')
    mutate('payments-subscription')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/subscriptions/{id}/increment_usage/
 */
export function useCreatePaymentsSubscriptionsIncrementUsage() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createPaymentsSubscriptionsIncrementUsage(id, data)

    // Revalidate related queries
    mutate('payments-subscriptions-increment-usage')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/subscriptions/{id}/update_status/
 */
export function useCreatePaymentsSubscriptionsUpdateStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createPaymentsSubscriptionsUpdateStatus(id, data)

    // Revalidate related queries
    mutate('payments-subscriptions-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/
 */
export function useCreatePaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createPaymentsUsers(data)

    // Revalidate related queries
    mutate('payments-users')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /payments/users/{id}/
 */
export function useUpdatePaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.updatePaymentsUsers(id, data)

    // Revalidate related queries
    mutate('payments-users')
    mutate('payments-user')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /payments/users/{id}/
 */
export function usePartialUpdatePaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<Payment> => {
    const result = await Fetchers.partialUpdatePaymentsUsers(id)

    // Revalidate related queries
    mutate('payments-users-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /payments/users/{id}/
 */
export function useDeletePaymentsUsers() {
  const { mutate } = useSWRConfig()

  return async (id: string): Promise<void> => {
    const result = await Fetchers.deletePaymentsUsers(id)

    // Revalidate related queries
    mutate('payments-users')
    mutate('payments-user')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{id}/cancel/
 */
export function useCreatePaymentsUsersCancel() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createPaymentsUsersCancel(id, data)

    // Revalidate related queries
    mutate('payments-users-cancel')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{id}/check_status/
 */
export function useCreatePaymentsUsersCheckStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createPaymentsUsersCheckStatus(id, data)

    // Revalidate related queries
    mutate('payments-users-check-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/api-keys/
 */
export function useCreatePaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (user_pk: number, data: APIKeyCreateRequest): Promise<APIKeyCreate> => {
    const result = await Fetchers.createPaymentsUsersApiKeys(user_pk, data)

    // Revalidate related queries
    mutate('payments-users-api-keys')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export function useUpdatePaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: APIKeyUpdateRequest): Promise<APIKeyUpdate> => {
    const result = await Fetchers.updatePaymentsUsersApiKeys(id, user_pk, data)

    // Revalidate related queries
    mutate('payments-users-api-keys')
    mutate('payments-users-api-key')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export function usePartialUpdatePaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<APIKeyUpdate> => {
    const result = await Fetchers.partialUpdatePaymentsUsersApiKeys(id, user_pk)

    // Revalidate related queries
    mutate('payments-users-api-keys-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export function useDeletePaymentsUsersApiKeys() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<void> => {
    const result = await Fetchers.deletePaymentsUsersApiKeys(id, user_pk)

    // Revalidate related queries
    mutate('payments-users-api-keys')
    mutate('payments-users-api-key')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/api-keys/{id}/perform_action/
 */
export function useCreatePaymentsUsersApiKeysPerformAction() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<APIKeyDetail> => {
    const result = await Fetchers.createPaymentsUsersApiKeysPerformAction(id, user_pk)

    // Revalidate related queries
    mutate('payments-users-api-keys-perform-action')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/payments/
 */
export function useCreatePaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (user_pk: number, data: PaymentCreateRequest): Promise<PaymentCreate> => {
    const result = await Fetchers.createPaymentsUsersPayments(user_pk, data)

    // Revalidate related queries
    mutate('payments-users-payments')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export function useUpdatePaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.updatePaymentsUsersPayments(id, user_pk, data)

    // Revalidate related queries
    mutate('payments-users-payments')
    mutate('payments-users-payment')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export function usePartialUpdatePaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<Payment> => {
    const result = await Fetchers.partialUpdatePaymentsUsersPayments(id, user_pk)

    // Revalidate related queries
    mutate('payments-users-payments-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export function useDeletePaymentsUsersPayments() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<void> => {
    const result = await Fetchers.deletePaymentsUsersPayments(id, user_pk)

    // Revalidate related queries
    mutate('payments-users-payments')
    mutate('payments-users-payment')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/payments/{id}/cancel/
 */
export function useCreatePaymentsUsersPaymentsCancel() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createPaymentsUsersPaymentsCancel(id, user_pk, data)

    // Revalidate related queries
    mutate('payments-users-payments-cancel')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/payments/{id}/check_status/
 */
export function useCreatePaymentsUsersPaymentsCheckStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: PaymentRequest): Promise<Payment> => {
    const result = await Fetchers.createPaymentsUsersPaymentsCheckStatus(id, user_pk, data)

    // Revalidate related queries
    mutate('payments-users-payments-check-status')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/subscriptions/
 */
export function useCreatePaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (user_pk: number, data: SubscriptionCreateRequest): Promise<SubscriptionCreate> => {
    const result = await Fetchers.createPaymentsUsersSubscriptions(user_pk, data)

    // Revalidate related queries
    mutate('payments-users-subscriptions')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export function useUpdatePaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.updatePaymentsUsersSubscriptions(id, user_pk, data)

    // Revalidate related queries
    mutate('payments-users-subscriptions')
    mutate('payments-users-subscription')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export function usePartialUpdatePaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<Subscription> => {
    const result = await Fetchers.partialUpdatePaymentsUsersSubscriptions(id, user_pk)

    // Revalidate related queries
    mutate('payments-users-subscriptions-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export function useDeletePaymentsUsersSubscriptions() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number): Promise<void> => {
    const result = await Fetchers.deletePaymentsUsersSubscriptions(id, user_pk)

    // Revalidate related queries
    mutate('payments-users-subscriptions')
    mutate('payments-users-subscription')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/subscriptions/{id}/increment_usage/
 */
export function useCreatePaymentsUsersSubscriptionsIncrementUsage() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createPaymentsUsersSubscriptionsIncrementUsage(id, user_pk, data)

    // Revalidate related queries
    mutate('payments-users-subscriptions-increment-usage')

    return result
  }
}

/**
 *
 * @method POST
 * @path /payments/users/{user_pk}/subscriptions/{id}/update_status/
 */
export function useCreatePaymentsUsersSubscriptionsUpdateStatus() {
  const { mutate } = useSWRConfig()

  return async (id: string, user_pk: number, data: SubscriptionRequest): Promise<Subscription> => {
    const result = await Fetchers.createPaymentsUsersSubscriptionsUpdateStatus(id, user_pk, data)

    // Revalidate related queries
    mutate('payments-users-subscriptions-status')

    return result
  }
}
