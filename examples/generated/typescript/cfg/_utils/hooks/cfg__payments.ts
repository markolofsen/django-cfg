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
export function usePaymentsApiKeys(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; user?: number }) {
  return useSWR<PaginatedAPIKeyListList>(
    params ? ['payments-api-keys', params] : 'payments-api-keys',
    () => Fetchers.getPaymentsApiKeys(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/{id}/
 */
export function usePaymentsApiKey(id: string) {
  return useSWR<APIKeyDetail>(
    ['payments-api-key', id],
    () => Fetchers.getPaymentsApiKey(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/analytics/
 */
export function usePaymentsApiKeysAnalytic() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-analytic',
    () => Fetchers.getPaymentsApiKeysAnalytic()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/by_user/
 */
export function usePaymentsApiKeysByUser() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-by-user',
    () => Fetchers.getPaymentsApiKeysByUser()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/expiring_soon/
 */
export function usePaymentsApiKeysExpiringSoon() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-expiring-soon',
    () => Fetchers.getPaymentsApiKeysExpiringSoon()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/health/
 */
export function usePaymentsApiKeysHealth() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-health',
    () => Fetchers.getPaymentsApiKeysHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/api-keys/stats/
 */
export function usePaymentsApiKeysStat() {
  return useSWR<APIKeyDetail>(
    'payments-api-keys-stat',
    () => Fetchers.getPaymentsApiKeysStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/
 */
export function usePaymentsBalances(params?: { ordering?: string; page?: number; page_size?: number; search?: string; user?: number }) {
  return useSWR<PaginatedUserBalanceList>(
    params ? ['payments-balances', params] : 'payments-balances',
    () => Fetchers.getPaymentsBalances(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/{id}/
 */
export function usePaymentsBalance(id: number) {
  return useSWR<UserBalance>(
    ['payments-balance', id],
    () => Fetchers.getPaymentsBalance(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/analytics/
 */
export function usePaymentsBalancesAnalytic() {
  return useSWR<UserBalance>(
    'payments-balances-analytic',
    () => Fetchers.getPaymentsBalancesAnalytic()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/health/
 */
export function usePaymentsBalancesHealth() {
  return useSWR<UserBalance>(
    'payments-balances-health',
    () => Fetchers.getPaymentsBalancesHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/stats/
 */
export function usePaymentsBalancesStat() {
  return useSWR<UserBalance>(
    'payments-balances-stat',
    () => Fetchers.getPaymentsBalancesStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/balances/summary/
 */
export function usePaymentsBalancesSummary() {
  return useSWR<UserBalance>(
    'payments-balances-summary',
    () => Fetchers.getPaymentsBalancesSummary()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/
 */
export function usePaymentsCurrencies(params?: { currency_type?: string; is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedCurrencyListList>(
    params ? ['payments-currencies', params] : 'payments-currencies',
    () => Fetchers.getPaymentsCurrencies(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/{id}/
 */
export function usePaymentsCurrencie(id: number) {
  return useSWR<Currency>(
    ['payments-currencie', id],
    () => Fetchers.getPaymentsCurrencie(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/{id}/networks/
 */
export function usePaymentsCurrenciesNetwork(id: number) {
  return useSWR<Currency>(
    ['payments-currencies-network', id],
    () => Fetchers.getPaymentsCurrenciesNetwork(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/{id}/providers/
 */
export function usePaymentsCurrenciesProvider(id: number) {
  return useSWR<Currency>(
    ['payments-currencies-provider', id],
    () => Fetchers.getPaymentsCurrenciesProvider(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/crypto/
 */
export function usePaymentsCurrenciesCrypto() {
  return useSWR<Currency>(
    'payments-currencies-crypto',
    () => Fetchers.getPaymentsCurrenciesCrypto()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/fiat/
 */
export function usePaymentsCurrenciesFiat() {
  return useSWR<Currency>(
    'payments-currencies-fiat',
    () => Fetchers.getPaymentsCurrenciesFiat()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/health/
 */
export function usePaymentsCurrenciesHealth() {
  return useSWR<Currency>(
    'payments-currencies-health',
    () => Fetchers.getPaymentsCurrenciesHealth()
  )
}

/**
 * Get exchange rates
 *
 * @method GET
 * @path /payments/currencies/rates/
 */
export function usePaymentsCurrenciesRate(params: { base_currency: string; currencies: string }) {
  return useSWR<Currency>(
    params ? ['payments-currencies-rate', params] : 'payments-currencies-rate',
    () => Fetchers.getPaymentsCurrenciesRate(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/stable/
 */
export function usePaymentsCurrenciesStable() {
  return useSWR<Currency>(
    'payments-currencies-stable',
    () => Fetchers.getPaymentsCurrenciesStable()
  )
}

/**
 *
 * @method GET
 * @path /payments/currencies/stats/
 */
export function usePaymentsCurrenciesStat() {
  return useSWR<Currency>(
    'payments-currencies-stat',
    () => Fetchers.getPaymentsCurrenciesStat()
  )
}

/**
 * Get supported currencies
 *
 * @method GET
 * @path /payments/currencies/supported/
 */
export function usePaymentsCurrenciesSupported(params?: { currency_type?: string; provider?: string }) {
  return useSWR<Currency>(
    params ? ['payments-currencies-supported', params] : 'payments-currencies-supported',
    () => Fetchers.getPaymentsCurrenciesSupported(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/
 */
export function usePaymentsEndpointGroups(params?: { is_enabled?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedEndpointGroupList>(
    params ? ['payments-endpoint-groups', params] : 'payments-endpoint-groups',
    () => Fetchers.getPaymentsEndpointGroups(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/{id}/
 */
export function usePaymentsEndpointGroup(id: number) {
  return useSWR<EndpointGroup>(
    ['payments-endpoint-group', id],
    () => Fetchers.getPaymentsEndpointGroup(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/available/
 */
export function usePaymentsEndpointGroupsAvailable() {
  return useSWR<EndpointGroup>(
    'payments-endpoint-groups-available',
    () => Fetchers.getPaymentsEndpointGroupsAvailable()
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/health/
 */
export function usePaymentsEndpointGroupsHealth() {
  return useSWR<EndpointGroup>(
    'payments-endpoint-groups-health',
    () => Fetchers.getPaymentsEndpointGroupsHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/endpoint-groups/stats/
 */
export function usePaymentsEndpointGroupsStat() {
  return useSWR<EndpointGroup>(
    'payments-endpoint-groups-stat',
    () => Fetchers.getPaymentsEndpointGroupsStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/health/
 */
export function usePaymentsHealth() {
  return useSWR<Payment>(
    'payments-health',
    () => Fetchers.getPaymentsHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/
 */
export function usePaymentsNetworks(params?: { is_active?: boolean; native_currency__code?: string; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedNetworkList>(
    params ? ['payments-networks', params] : 'payments-networks',
    () => Fetchers.getPaymentsNetworks(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/{id}/
 */
export function usePaymentsNetwork(id: number) {
  return useSWR<Network>(
    ['payments-network', id],
    () => Fetchers.getPaymentsNetwork(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/by_currency/
 */
export function usePaymentsNetworksByCurrency() {
  return useSWR<Network>(
    'payments-networks-by-currency',
    () => Fetchers.getPaymentsNetworksByCurrency()
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/health/
 */
export function usePaymentsNetworksHealth() {
  return useSWR<Network>(
    'payments-networks-health',
    () => Fetchers.getPaymentsNetworksHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/networks/stats/
 */
export function usePaymentsNetworksStat() {
  return useSWR<Network>(
    'payments-networks-stat',
    () => Fetchers.getPaymentsNetworksStat()
  )
}

/**
 * API Keys Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/api_keys_overview/
 */
export function usePaymentsOverviewDashboardApiKeysOverview() {
  return useSWR<APIKeysOverview>(
    'payments-overview-dashboard-api-keys-overview',
    () => Fetchers.getPaymentsOverviewDashboardApiKeysOverview()
  )
}

/**
 * Balance Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/balance_overview/
 */
export function usePaymentsOverviewDashboardBalanceOverview() {
  return useSWR<BalanceOverview>(
    'payments-overview-dashboard-balance-overview',
    () => Fetchers.getPaymentsOverviewDashboardBalanceOverview()
  )
}

/**
 * Payments Chart Data
 *
 * @method GET
 * @path /payments/overview/dashboard/chart_data/
 */
export function usePaymentsOverviewDashboardChartData(params?: { period?: string }) {
  return useSWR<PaymentsChartResponse>(
    params ? ['payments-overview-dashboard-chart-data', params] : 'payments-overview-dashboard-chart-data',
    () => Fetchers.getPaymentsOverviewDashboardChartData(params)
  )
}

/**
 * Payments Dashboard Metrics
 *
 * @method GET
 * @path /payments/overview/dashboard/metrics/
 */
export function usePaymentsOverviewDashboardMetric() {
  return useSWR<PaymentsMetrics>(
    'payments-overview-dashboard-metric',
    () => Fetchers.getPaymentsOverviewDashboardMetric()
  )
}

/**
 * Payments Dashboard Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/overview/
 */
export function usePaymentsOverviewDashboardOverview() {
  return useSWR<PaymentsDashboardOverview>(
    'payments-overview-dashboard-overview',
    () => Fetchers.getPaymentsOverviewDashboardOverview()
  )
}

/**
 * Payment Analytics
 *
 * @method GET
 * @path /payments/overview/dashboard/payment_analytics/
 */
export function usePaymentsOverviewDashboardPaymentAnalytic(params?: { limit?: number }) {
  return useSWR<PaymentAnalyticsResponse>(
    params ? ['payments-overview-dashboard-payment-analytic', params] : 'payments-overview-dashboard-payment-analytic',
    () => Fetchers.getPaymentsOverviewDashboardPaymentAnalytic(params)
  )
}

/**
 * Recent Payments
 *
 * @method GET
 * @path /payments/overview/dashboard/recent_payments/
 */
export function usePaymentsOverviewDashboardRecentPayments(params?: { limit?: number; page?: number; page_size?: number }) {
  return useSWR<PaginatedRecentPaymentList>(
    params ? ['payments-overview-dashboard-recent-payments', params] : 'payments-overview-dashboard-recent-payments',
    () => Fetchers.getPaymentsOverviewDashboardRecentPayments(params)
  )
}

/**
 * Recent Transactions
 *
 * @method GET
 * @path /payments/overview/dashboard/recent_transactions/
 */
export function usePaymentsOverviewDashboardRecentTransactions(params?: { limit?: number; page?: number; page_size?: number }) {
  return useSWR<PaginatedRecentTransactionList>(
    params ? ['payments-overview-dashboard-recent-transactions', params] : 'payments-overview-dashboard-recent-transactions',
    () => Fetchers.getPaymentsOverviewDashboardRecentTransactions(params)
  )
}

/**
 * Subscription Overview
 *
 * @method GET
 * @path /payments/overview/dashboard/subscription_overview/
 */
export function usePaymentsOverviewDashboardSubscriptionOverview() {
  return useSWR<SubscriptionOverview>(
    'payments-overview-dashboard-subscription-overview',
    () => Fetchers.getPaymentsOverviewDashboardSubscriptionOverview()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/
 */
export function usePaymentsPayments(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number }) {
  return useSWR<PaginatedPaymentListList>(
    params ? ['payments-payments', params] : 'payments-payments',
    () => Fetchers.getPaymentsPayments(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/{id}/
 */
export function usePaymentsPayment(id: string) {
  return useSWR<Payment>(
    ['payments-payment', id],
    () => Fetchers.getPaymentsPayment(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/analytics/
 */
export function usePaymentsPaymentsAnalytic() {
  return useSWR<Payment>(
    'payments-payments-analytic',
    () => Fetchers.getPaymentsPaymentsAnalytic()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/by_provider/
 */
export function usePaymentsPaymentsByProvider() {
  return useSWR<Payment>(
    'payments-payments-by-provider',
    () => Fetchers.getPaymentsPaymentsByProvider()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/health/
 */
export function usePaymentsPaymentsHealth() {
  return useSWR<Payment>(
    'payments-payments-health',
    () => Fetchers.getPaymentsPaymentsHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/stats/
 */
export function usePaymentsPaymentsStat() {
  return useSWR<Payment>(
    'payments-payments-stat',
    () => Fetchers.getPaymentsPaymentsStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/payments/status/{id}/
 */
export function usePaymentsPaymentsStatu(id: string) {
  return useSWR<Payment>(
    ['payments-payments-statu', id],
    () => Fetchers.getPaymentsPaymentsStatu(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/
 */
export function usePaymentsProviderCurrencies(params?: { currency__code?: string; is_enabled?: boolean; network__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string }) {
  return useSWR<PaginatedProviderCurrencyList>(
    params ? ['payments-provider-currencies', params] : 'payments-provider-currencies',
    () => Fetchers.getPaymentsProviderCurrencies(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/{id}/
 */
export function usePaymentsProviderCurrencie(id: number) {
  return useSWR<ProviderCurrency>(
    ['payments-provider-currencie', id],
    () => Fetchers.getPaymentsProviderCurrencie(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/by_provider/
 */
export function usePaymentsProviderCurrenciesByProvider() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-by-provider',
    () => Fetchers.getPaymentsProviderCurrenciesByProvider()
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/health/
 */
export function usePaymentsProviderCurrenciesHealth() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-health',
    () => Fetchers.getPaymentsProviderCurrenciesHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/limits/
 */
export function usePaymentsProviderCurrenciesLimit() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-limit',
    () => Fetchers.getPaymentsProviderCurrenciesLimit()
  )
}

/**
 *
 * @method GET
 * @path /payments/provider-currencies/stats/
 */
export function usePaymentsProviderCurrenciesStat() {
  return useSWR<ProviderCurrency>(
    'payments-provider-currencies-stat',
    () => Fetchers.getPaymentsProviderCurrenciesStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/
 */
export function usePaymentsSubscriptions(params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string; user?: number }) {
  return useSWR<PaginatedSubscriptionListList>(
    params ? ['payments-subscriptions', params] : 'payments-subscriptions',
    () => Fetchers.getPaymentsSubscriptions(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/{id}/
 */
export function usePaymentsSubscription(id: string) {
  return useSWR<Subscription>(
    ['payments-subscription', id],
    () => Fetchers.getPaymentsSubscription(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/analytics/
 */
export function usePaymentsSubscriptionsAnalytic() {
  return useSWR<Subscription>(
    'payments-subscriptions-analytic',
    () => Fetchers.getPaymentsSubscriptionsAnalytic()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/by_status/
 */
export function usePaymentsSubscriptionsByStatu() {
  return useSWR<Subscription>(
    'payments-subscriptions-by-statu',
    () => Fetchers.getPaymentsSubscriptionsByStatu()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/by_tier/
 */
export function usePaymentsSubscriptionsByTier() {
  return useSWR<Subscription>(
    'payments-subscriptions-by-tier',
    () => Fetchers.getPaymentsSubscriptionsByTier()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/health/
 */
export function usePaymentsSubscriptionsHealth() {
  return useSWR<Subscription>(
    'payments-subscriptions-health',
    () => Fetchers.getPaymentsSubscriptionsHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/subscriptions/stats/
 */
export function usePaymentsSubscriptionsStat() {
  return useSWR<Subscription>(
    'payments-subscriptions-stat',
    () => Fetchers.getPaymentsSubscriptionsStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/
 */
export function usePaymentsTariffs(params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedTariffList>(
    params ? ['payments-tariffs', params] : 'payments-tariffs',
    () => Fetchers.getPaymentsTariffs(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/{id}/
 */
export function usePaymentsTariff(id: number) {
  return useSWR<Tariff>(
    ['payments-tariff', id],
    () => Fetchers.getPaymentsTariff(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/{id}/endpoint_groups/
 */
export function usePaymentsTariffsEndpointGroup(id: number) {
  return useSWR<Tariff>(
    ['payments-tariffs-endpoint-group', id],
    () => Fetchers.getPaymentsTariffsEndpointGroup(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/free/
 */
export function usePaymentsTariffsFree() {
  return useSWR<Tariff>(
    'payments-tariffs-free',
    () => Fetchers.getPaymentsTariffsFree()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/health/
 */
export function usePaymentsTariffsHealth() {
  return useSWR<Tariff>(
    'payments-tariffs-health',
    () => Fetchers.getPaymentsTariffsHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/paid/
 */
export function usePaymentsTariffsPaid() {
  return useSWR<Tariff>(
    'payments-tariffs-paid',
    () => Fetchers.getPaymentsTariffsPaid()
  )
}

/**
 *
 * @method GET
 * @path /payments/tariffs/stats/
 */
export function usePaymentsTariffsStat() {
  return useSWR<Tariff>(
    'payments-tariffs-stat',
    () => Fetchers.getPaymentsTariffsStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/
 */
export function usePaymentsTransactions(params?: { ordering?: string; page?: number; page_size?: number; payment_id?: string; search?: string; transaction_type?: string; user?: number }) {
  return useSWR<PaginatedTransactionList>(
    params ? ['payments-transactions', params] : 'payments-transactions',
    () => Fetchers.getPaymentsTransactions(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/{id}/
 */
export function usePaymentsTransaction(id: string) {
  return useSWR<Transaction>(
    ['payments-transaction', id],
    () => Fetchers.getPaymentsTransaction(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/by_type/
 */
export function usePaymentsTransactionsByType() {
  return useSWR<Transaction>(
    'payments-transactions-by-type',
    () => Fetchers.getPaymentsTransactionsByType()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/health/
 */
export function usePaymentsTransactionsHealth() {
  return useSWR<Transaction>(
    'payments-transactions-health',
    () => Fetchers.getPaymentsTransactionsHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/recent/
 */
export function usePaymentsTransactionsRecent() {
  return useSWR<Transaction>(
    'payments-transactions-recent',
    () => Fetchers.getPaymentsTransactionsRecent()
  )
}

/**
 *
 * @method GET
 * @path /payments/transactions/stats/
 */
export function usePaymentsTransactionsStat() {
  return useSWR<Transaction>(
    'payments-transactions-stat',
    () => Fetchers.getPaymentsTransactionsStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/users/
 */
export function usePaymentsUsers(params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }) {
  return useSWR<PaginatedPaymentListList>(
    params ? ['payments-users', params] : 'payments-users',
    () => Fetchers.getPaymentsUsers(params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{id}/
 */
export function usePaymentsUser(id: string) {
  return useSWR<Payment>(
    ['payments-user', id],
    () => Fetchers.getPaymentsUser(id)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/
 */
export function usePaymentsUsersApiKeys(user_pk: number, params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedAPIKeyListList>(
    ['payments-users-api-keys', user_pk],
    () => Fetchers.getPaymentsUsersApiKeys(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/{id}/
 */
export function usePaymentsUsersApiKey(id: string, user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-key', id],
    () => Fetchers.getPaymentsUsersApiKey(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/active/
 */
export function usePaymentsUsersApiKeysActive(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-active', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysActive(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/health/
 */
export function usePaymentsUsersApiKeysHealth(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-health', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysHealth(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/stats/
 */
export function usePaymentsUsersApiKeysStat(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-stat', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysStat(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/api-keys/summary/
 */
export function usePaymentsUsersApiKeysSummary(user_pk: number) {
  return useSWR<APIKeyDetail>(
    ['payments-users-api-keys-summary', user_pk],
    () => Fetchers.getPaymentsUsersApiKeysSummary(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/
 */
export function usePaymentsUsersPayments(user_pk: number, params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string }) {
  return useSWR<PaginatedPaymentListList>(
    ['payments-users-payments', user_pk],
    () => Fetchers.getPaymentsUsersPayments(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/{id}/
 */
export function usePaymentsUsersPayment(id: string, user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payment', id],
    () => Fetchers.getPaymentsUsersPayment(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/health/
 */
export function usePaymentsUsersPaymentsHealth(user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payments-health', user_pk],
    () => Fetchers.getPaymentsUsersPaymentsHealth(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/stats/
 */
export function usePaymentsUsersPaymentsStat(user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payments-stat', user_pk],
    () => Fetchers.getPaymentsUsersPaymentsStat(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/payments/summary/
 */
export function usePaymentsUsersPaymentsSummary(user_pk: number) {
  return useSWR<Payment>(
    ['payments-users-payments-summary', user_pk],
    () => Fetchers.getPaymentsUsersPaymentsSummary(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/
 */
export function usePaymentsUsersSubscriptions(user_pk: number, params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string }) {
  return useSWR<PaginatedSubscriptionListList>(
    ['payments-users-subscriptions', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptions(user_pk, params)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/{id}/
 */
export function usePaymentsUsersSubscription(id: string, user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscription', id],
    () => Fetchers.getPaymentsUsersSubscription(id, user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/active/
 */
export function usePaymentsUsersSubscriptionsActive(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-active', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsActive(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/health/
 */
export function usePaymentsUsersSubscriptionsHealth(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-health', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsHealth(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/stats/
 */
export function usePaymentsUsersSubscriptionsStat(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-stat', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsStat(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/{user_pk}/subscriptions/summary/
 */
export function usePaymentsUsersSubscriptionsSummary(user_pk: number) {
  return useSWR<Subscription>(
    ['payments-users-subscriptions-summary', user_pk],
    () => Fetchers.getPaymentsUsersSubscriptionsSummary(user_pk)
  )
}

/**
 *
 * @method GET
 * @path /payments/users/health/
 */
export function usePaymentsUsersHealth() {
  return useSWR<Payment>(
    'payments-users-health',
    () => Fetchers.getPaymentsUsersHealth()
  )
}

/**
 *
 * @method GET
 * @path /payments/users/stats/
 */
export function usePaymentsUsersStat() {
  return useSWR<Payment>(
    'payments-users-stat',
    () => Fetchers.getPaymentsUsersStat()
  )
}

/**
 *
 * @method GET
 * @path /payments/users/summary/
 */
export function usePaymentsUsersSummary() {
  return useSWR<Payment>(
    'payments-users-summary',
    () => Fetchers.getPaymentsUsersSummary()
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
