/**
 * Typed fetchers for Cfg Payments
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
import { AdminPaymentCreateSchema, type AdminPaymentCreate } from '../schemas/AdminPaymentCreate.schema'
import { AdminPaymentCreateRequestSchema, type AdminPaymentCreateRequest } from '../schemas/AdminPaymentCreateRequest.schema'
import { AdminPaymentDetailSchema, type AdminPaymentDetail } from '../schemas/AdminPaymentDetail.schema'
import { AdminPaymentStatsSchema, type AdminPaymentStats } from '../schemas/AdminPaymentStats.schema'
import { AdminPaymentUpdateSchema, type AdminPaymentUpdate } from '../schemas/AdminPaymentUpdate.schema'
import { AdminPaymentUpdateRequestSchema, type AdminPaymentUpdateRequest } from '../schemas/AdminPaymentUpdateRequest.schema'
import { AdminUserSchema, type AdminUser } from '../schemas/AdminUser.schema'
import { BalanceOverviewSchema, type BalanceOverview } from '../schemas/BalanceOverview.schema'
import { CurrencySchema, type Currency } from '../schemas/Currency.schema'
import { EndpointGroupSchema, type EndpointGroup } from '../schemas/EndpointGroup.schema'
import { NetworkSchema, type Network } from '../schemas/Network.schema'
import { PaginatedAPIKeyListListSchema, type PaginatedAPIKeyListList } from '../schemas/PaginatedAPIKeyListList.schema'
import { PaginatedAdminPaymentListListSchema, type PaginatedAdminPaymentListList } from '../schemas/PaginatedAdminPaymentListList.schema'
import { PaginatedAdminPaymentStatsListSchema, type PaginatedAdminPaymentStatsList } from '../schemas/PaginatedAdminPaymentStatsList.schema'
import { PaginatedAdminUserListSchema, type PaginatedAdminUserList } from '../schemas/PaginatedAdminUserList.schema'
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
import { PaginatedWebhookEventListListSchema, type PaginatedWebhookEventListList } from '../schemas/PaginatedWebhookEventListList.schema'
import { PaginatedWebhookStatsListSchema, type PaginatedWebhookStatsList } from '../schemas/PaginatedWebhookStatsList.schema'
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
import { WebhookEventListSchema, type WebhookEventList } from '../schemas/WebhookEventList.schema'
import { WebhookEventListRequestSchema, type WebhookEventListRequest } from '../schemas/WebhookEventListRequest.schema'
import { WebhookStatsSchema, type WebhookStats } from '../schemas/WebhookStats.schema'
import { WebhookStatsRequestSchema, type WebhookStatsRequest } from '../schemas/WebhookStatsRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * getCfgPaymentsAdminApiPaymentsList
 *
 * Admin ViewSet for payment management.
 * 
 * Provides full CRUD operations for payments with admin-specific features.
 *
 * @method GET
 * @path /cfg/payments/admin/api/payments/
 */
export async function getCfgPaymentsAdminApiPaymentsList(
  params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number },
  client?: API
): Promise<PaginatedAdminPaymentListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsList(params?.currency__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search, params?.status, params?.user)
  return PaginatedAdminPaymentListListSchema.parse(response)
}

/**
 * createCfgPaymentsAdminApiPayments
 *
 * Create payment with enhanced error handling.
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/
 */
export async function createCfgPaymentsAdminApiPayments(
  data: AdminPaymentCreateRequest,
  client?: API
): Promise<AdminPaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsCreate(data)
  return AdminPaymentCreateSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiPaymentsById
 *
 * Admin ViewSet for payment management.
 * 
 * Provides full CRUD operations for payments with admin-specific features.
 *
 * @method GET
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export async function getCfgPaymentsAdminApiPaymentsById(
  id: string,
  client?: API
): Promise<AdminPaymentDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsRetrieve(id)
  return AdminPaymentDetailSchema.parse(response)
}

/**
 * updateCfgPaymentsAdminApiPayments
 *
 * Admin ViewSet for payment management.
 * 
 * Provides full CRUD operations for payments with admin-specific features.
 *
 * @method PUT
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export async function updateCfgPaymentsAdminApiPayments(
  id: string, data: AdminPaymentUpdateRequest,
  client?: API
): Promise<AdminPaymentUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsUpdate(id, data)
  return AdminPaymentUpdateSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsAdminApiPayments
 *
 * Admin ViewSet for payment management.
 * 
 * Provides full CRUD operations for payments with admin-specific features.
 *
 * @method PATCH
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export async function partialUpdateCfgPaymentsAdminApiPayments(
  id: string,
  client?: API
): Promise<AdminPaymentUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsPartialUpdate(id)
  return AdminPaymentUpdateSchema.parse(response)
}

/**
 * deleteCfgPaymentsAdminApiPayments
 *
 * Admin ViewSet for payment management.
 * 
 * Provides full CRUD operations for payments with admin-specific features.
 *
 * @method DELETE
 * @path /cfg/payments/admin/api/payments/{id}/
 */
export async function deleteCfgPaymentsAdminApiPayments(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsDestroy(id)
  return response
}

/**
 * createCfgPaymentsAdminApiPaymentsCancel
 *
 * Cancel a payment.
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/{id}/cancel/
 */
export async function createCfgPaymentsAdminApiPaymentsCancel(
  id: string,
  client?: API
): Promise<AdminPaymentDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsCancelCreate(id)
  return AdminPaymentDetailSchema.parse(response)
}

/**
 * createCfgPaymentsAdminApiPaymentsRefreshStatus
 *
 * Refresh payment status from provider via AJAX.
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/{id}/refresh_status/
 */
export async function createCfgPaymentsAdminApiPaymentsRefreshStatus(
  id: string,
  client?: API
): Promise<AdminPaymentDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsRefreshStatusCreate(id)
  return AdminPaymentDetailSchema.parse(response)
}

/**
 * createCfgPaymentsAdminApiPaymentsRefund
 *
 * Refund a payment.
 *
 * @method POST
 * @path /cfg/payments/admin/api/payments/{id}/refund/
 */
export async function createCfgPaymentsAdminApiPaymentsRefund(
  id: string,
  client?: API
): Promise<AdminPaymentDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsRefundCreate(id)
  return AdminPaymentDetailSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiPaymentsStatsById
 *
 * Get comprehensive payment statistics.
 *
 * @method GET
 * @path /cfg/payments/admin/api/payments/stats/
 */
export async function getCfgPaymentsAdminApiPaymentsStatsById(
  client?: API
): Promise<AdminPaymentStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiPaymentsStatsRetrieve()
  return AdminPaymentStatsSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiStatsList
 *
 * Get overview statistics.
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/
 */
export async function getCfgPaymentsAdminApiStatsList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedAdminPaymentStatsList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiStatsList(params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedAdminPaymentStatsListSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiStatsById
 *
 * Admin ViewSet for comprehensive system statistics.
 * 
 * Provides aggregated statistics across all system components.
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/{id}/
 */
export async function getCfgPaymentsAdminApiStatsById(
  id: string,
  client?: API
): Promise<AdminPaymentStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiStatsRetrieve(id)
  return AdminPaymentStatsSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiStatsPaymentsById
 *
 * Get detailed payment statistics.
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/payments/
 */
export async function getCfgPaymentsAdminApiStatsPaymentsById(
  client?: API
): Promise<AdminPaymentStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiStatsPaymentsRetrieve()
  return AdminPaymentStatsSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiStatsSystemById
 *
 * Get system health and performance statistics.
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/system/
 */
export async function getCfgPaymentsAdminApiStatsSystemById(
  client?: API
): Promise<AdminPaymentStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiStatsSystemRetrieve()
  return AdminPaymentStatsSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiStatsWebhooksById
 *
 * Get detailed webhook statistics.
 *
 * @method GET
 * @path /cfg/payments/admin/api/stats/webhooks/
 */
export async function getCfgPaymentsAdminApiStatsWebhooksById(
  client?: API
): Promise<AdminPaymentStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiStatsWebhooksRetrieve()
  return AdminPaymentStatsSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiUsersList
 *
 * Override list to limit results for dropdown.
 *
 * @method GET
 * @path /cfg/payments/admin/api/users/
 */
export async function getCfgPaymentsAdminApiUsersList(
  params?: { is_active?: boolean; is_staff?: boolean; is_superuser?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedAdminUserList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiUsersList(params?.is_active, params?.is_staff, params?.is_superuser, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedAdminUserListSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiUsersById
 *
 * Admin ViewSet for user management.
 * 
 * Provides read-only access to users for admin interface.
 *
 * @method GET
 * @path /cfg/payments/admin/api/users/{id}/
 */
export async function getCfgPaymentsAdminApiUsersById(
  id: number,
  client?: API
): Promise<AdminUser> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiUsersRetrieve(id)
  return AdminUserSchema.parse(response)
}

/**
 * createCfgPaymentsAdminApiWebhookTestTest
 *
 * Test webhook endpoint.
 * 
 * Sends a test webhook to the specified URL with the given event type.
 * Useful for developers to test their webhook implementations.
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhook-test/test/
 */
export async function createCfgPaymentsAdminApiWebhookTestTest(
  data: WebhookStatsRequest,
  client?: API
): Promise<WebhookStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhookTestTestCreate(data)
  return WebhookStatsSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiWebhooksList
 *
 * List webhook providers and configurations with real ngrok URLs.
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/
 */
export async function getCfgPaymentsAdminApiWebhooksList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedWebhookStatsList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksList(params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedWebhookStatsListSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiWebhooksById
 *
 * Admin ViewSet for webhook configuration management.
 * 
 * Read-only view for webhook configurations and provider info.
 * Requires admin permissions.
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/{id}/
 */
export async function getCfgPaymentsAdminApiWebhooksById(
  id: string,
  client?: API
): Promise<WebhookStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksRetrieve(id)
  return WebhookStatsSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiWebhooksEventsList
 *
 * List webhook events with filtering and pagination.
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/
 */
export async function getCfgPaymentsAdminApiWebhooksEventsList(
  webhook_pk: string, params?: { ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedWebhookEventListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksEventsList(webhook_pk, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedWebhookEventListListSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiWebhooksEventsById
 *
 * Admin ViewSet for webhook events management.
 * 
 * Provides listing, filtering, and actions for webhook events.
 * Requires admin permissions.
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/{id}/
 */
export async function getCfgPaymentsAdminApiWebhooksEventsById(
  id: string, webhook_pk: string,
  client?: API
): Promise<WebhookEventList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksEventsRetrieve(id, webhook_pk)
  return WebhookEventListSchema.parse(response)
}

/**
 * createCfgPaymentsAdminApiWebhooksEventsRetry
 *
 * Retry a failed webhook event.
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/{id}/retry/
 */
export async function createCfgPaymentsAdminApiWebhooksEventsRetry(
  id: string, webhook_pk: string, data: WebhookEventListRequest,
  client?: API
): Promise<WebhookEventList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksEventsRetryCreate(id, webhook_pk, data)
  return WebhookEventListSchema.parse(response)
}

/**
 * createCfgPaymentsAdminApiWebhooksEventsClearAll
 *
 * Clear all webhook events.
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/clear_all/
 */
export async function createCfgPaymentsAdminApiWebhooksEventsClearAll(
  webhook_pk: string, data: WebhookEventListRequest,
  client?: API
): Promise<WebhookEventList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksEventsClearAllCreate(webhook_pk, data)
  return WebhookEventListSchema.parse(response)
}

/**
 * createCfgPaymentsAdminApiWebhooksEventsRetryFailed
 *
 * Retry all failed webhook events.
 *
 * @method POST
 * @path /cfg/payments/admin/api/webhooks/{webhook_pk}/events/retry_failed/
 */
export async function createCfgPaymentsAdminApiWebhooksEventsRetryFailed(
  webhook_pk: string, data: WebhookEventListRequest,
  client?: API
): Promise<WebhookEventList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksEventsRetryFailedCreate(webhook_pk, data)
  return WebhookEventListSchema.parse(response)
}

/**
 * getCfgPaymentsAdminApiWebhooksStatsById
 *
 * Get webhook statistics.
 *
 * @method GET
 * @path /cfg/payments/admin/api/webhooks/stats/
 */
export async function getCfgPaymentsAdminApiWebhooksStatsById(
  client?: API
): Promise<WebhookStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsAdminApiWebhooksStatsRetrieve()
  return WebhookStatsSchema.parse(response)
}

/**
 * getCfgPaymentsApiKeysList
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method GET
 * @path /cfg/payments/api-keys/
 */
export async function getCfgPaymentsApiKeysList(
  params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; user?: number },
  client?: API
): Promise<PaginatedAPIKeyListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysList(params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search, params?.user)
  return PaginatedAPIKeyListListSchema.parse(response)
}

/**
 * createCfgPaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method POST
 * @path /cfg/payments/api-keys/
 */
export async function createCfgPaymentsApiKeys(
  data: APIKeyCreateRequest,
  client?: API
): Promise<APIKeyCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysCreate(data)
  return APIKeyCreateSchema.parse(response)
}

/**
 * getCfgPaymentsApiKeysById
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method GET
 * @path /cfg/payments/api-keys/{id}/
 */
export async function getCfgPaymentsApiKeysById(
  id: string,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysRetrieve(id)
  return APIKeyDetailSchema.parse(response)
}

/**
 * updateCfgPaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method PUT
 * @path /cfg/payments/api-keys/{id}/
 */
export async function updateCfgPaymentsApiKeys(
  id: string, data: APIKeyUpdateRequest,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysUpdate(id, data)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method PATCH
 * @path /cfg/payments/api-keys/{id}/
 */
export async function partialUpdateCfgPaymentsApiKeys(
  id: string,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysPartialUpdate(id)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * deleteCfgPaymentsApiKeys
 *
 * Global API Key ViewSet: /api/api-keys/
 * 
 * Provides admin-level access to all API keys with filtering and stats.
 *
 * @method DELETE
 * @path /cfg/payments/api-keys/{id}/
 */
export async function deleteCfgPaymentsApiKeys(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysDestroy(id)
  return response
}

/**
 * createCfgPaymentsApiKeysPerformAction
 *
 * Perform action on API key.
 * 
 * POST /api/api-keys/{id}/perform_action/
 *
 * @method POST
 * @path /cfg/payments/api-keys/{id}/perform_action/
 */
export async function createCfgPaymentsApiKeysPerformAction(
  id: string,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysPerformActionCreate(id)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsApiKeysAnalyticsById
 *
 * Get API key analytics.
 * 
 * GET /api/api-keys/analytics/?days=30
 *
 * @method GET
 * @path /cfg/payments/api-keys/analytics/
 */
export async function getCfgPaymentsApiKeysAnalyticsById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysAnalyticsRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsApiKeysByUserById
 *
 * Get API keys grouped by user.
 * 
 * GET /api/api-keys/by_user/
 *
 * @method GET
 * @path /cfg/payments/api-keys/by_user/
 */
export async function getCfgPaymentsApiKeysByUserById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysByUserRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * createCfgPaymentsApiKeysCreate
 *
 * Standalone API key creation endpoint: /api/api-keys/create/
 * 
 * Simplified endpoint for API key creation.
 *
 * @method POST
 * @path /cfg/payments/api-keys/create/
 */
export async function createCfgPaymentsApiKeysCreate(
  data: APIKeyCreateRequest,
  client?: API
): Promise<APIKeyCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysCreateCreate(data)
  return APIKeyCreateSchema.parse(response)
}

/**
 * getCfgPaymentsApiKeysExpiringSoonById
 *
 * Get API keys expiring soon.
 * 
 * GET /api/api-keys/expiring_soon/?days=7
 *
 * @method GET
 * @path /cfg/payments/api-keys/expiring_soon/
 */
export async function getCfgPaymentsApiKeysExpiringSoonById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysExpiringSoonRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsApiKeysHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/api-keys/health/
 */
export async function getCfgPaymentsApiKeysHealthById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysHealthRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsApiKeysStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/api-keys/stats/
 */
export async function getCfgPaymentsApiKeysStatsById(
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysStatsRetrieve()
  return APIKeyDetailSchema.parse(response)
}

/**
 * Validate API Key (Standalone)
 *
 * Standalone endpoint to validate an API key and return key information
 *
 * @method POST
 * @path /cfg/payments/api-keys/validate/
 */
export async function createCfgPaymentsApiKeysValidate(
  data: APIKeyValidationRequest,
  client?: API
): Promise<APIKeyValidationResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysValidateCreate(data)
  return APIKeyValidationResponseSchema.parse(response)
}

/**
 * Validate API Key
 *
 * Validate an API key and return key information
 *
 * @method POST
 * @path /cfg/payments/api-keys/validate_key/
 */
export async function createCfgPaymentsApiKeysValidateKey(
  data: APIKeyValidationRequest,
  client?: API
): Promise<APIKeyValidationResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsApiKeysValidateKeyCreate(data)
  return APIKeyValidationResponseSchema.parse(response)
}

/**
 * getCfgPaymentsBalancesList
 *
 * User balance ViewSet: /api/balances/
 * 
 * Read-only access to user balances with statistics.
 *
 * @method GET
 * @path /cfg/payments/balances/
 */
export async function getCfgPaymentsBalancesList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string; user?: number },
  client?: API
): Promise<PaginatedUserBalanceList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsBalancesList(params?.ordering, params?.page, params?.page_size, params?.search, params?.user)
  return PaginatedUserBalanceListSchema.parse(response)
}

/**
 * getCfgPaymentsBalancesById
 *
 * User balance ViewSet: /api/balances/
 * 
 * Read-only access to user balances with statistics.
 *
 * @method GET
 * @path /cfg/payments/balances/{id}/
 */
export async function getCfgPaymentsBalancesById(
  id: number,
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsBalancesRetrieve(id)
  return UserBalanceSchema.parse(response)
}

/**
 * getCfgPaymentsBalancesAnalyticsById
 *
 * Get balance analytics.
 * 
 * GET /api/balances/analytics/?days=30
 *
 * @method GET
 * @path /cfg/payments/balances/analytics/
 */
export async function getCfgPaymentsBalancesAnalyticsById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsBalancesAnalyticsRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getCfgPaymentsBalancesHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/balances/health/
 */
export async function getCfgPaymentsBalancesHealthById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsBalancesHealthRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getCfgPaymentsBalancesStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/balances/stats/
 */
export async function getCfgPaymentsBalancesStatsById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsBalancesStatsRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getCfgPaymentsBalancesSummaryById
 *
 * Get balance summary for all users.
 * 
 * GET /api/balances/summary/
 *
 * @method GET
 * @path /cfg/payments/balances/summary/
 */
export async function getCfgPaymentsBalancesSummaryById(
  client?: API
): Promise<UserBalance> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsBalancesSummaryRetrieve()
  return UserBalanceSchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesList
 *
 * Currency ViewSet: /api/currencies/
 * 
 * Read-only access to currency information with conversion capabilities.
 *
 * @method GET
 * @path /cfg/payments/currencies/
 */
export async function getCfgPaymentsCurrenciesList(
  params?: { currency_type?: string; is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedCurrencyListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesList(params?.currency_type, params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedCurrencyListListSchema.parse(response)
}

/**
 * createCfgPaymentsCurrencies
 *
 * Disable create action.
 *
 * @method POST
 * @path /cfg/payments/currencies/
 */
export async function createCfgPaymentsCurrencies(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesCreate()
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesById
 *
 * Currency ViewSet: /api/currencies/
 * 
 * Read-only access to currency information with conversion capabilities.
 *
 * @method GET
 * @path /cfg/payments/currencies/{id}/
 */
export async function getCfgPaymentsCurrenciesById(
  id: number,
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesRetrieve(id)
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesNetworksById
 *
 * Get networks for specific currency.
 * 
 * GET /api/currencies/{id}/networks/
 *
 * @method GET
 * @path /cfg/payments/currencies/{id}/networks/
 */
export async function getCfgPaymentsCurrenciesNetworksById(
  id: number,
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesNetworksRetrieve(id)
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesProvidersById
 *
 * Get providers supporting specific currency.
 * 
 * GET /api/currencies/{id}/providers/
 *
 * @method GET
 * @path /cfg/payments/currencies/{id}/providers/
 */
export async function getCfgPaymentsCurrenciesProvidersById(
  id: number,
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesProvidersRetrieve(id)
  return CurrencySchema.parse(response)
}

/**
 * createCfgPaymentsCurrenciesConvert
 *
 * Convert between currencies.
 * 
 * POST /api/currencies/convert/
 *
 * @method POST
 * @path /cfg/payments/currencies/convert/
 */
export async function createCfgPaymentsCurrenciesConvert(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesConvertCreate()
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesCryptoById
 *
 * Get only cryptocurrencies.
 * 
 * GET /api/currencies/crypto/
 *
 * @method GET
 * @path /cfg/payments/currencies/crypto/
 */
export async function getCfgPaymentsCurrenciesCryptoById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesCryptoRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesFiatById
 *
 * Get only fiat currencies.
 * 
 * GET /api/currencies/fiat/
 *
 * @method GET
 * @path /cfg/payments/currencies/fiat/
 */
export async function getCfgPaymentsCurrenciesFiatById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesFiatRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/currencies/health/
 */
export async function getCfgPaymentsCurrenciesHealthById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesHealthRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * Get exchange rates
 *
 * Get current exchange rates for specified currencies
 *
 * @method GET
 * @path /cfg/payments/currencies/rates/
 */
export async function getCfgPaymentsCurrenciesRatesById(
  params: { base_currency: string; currencies: string },
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesRatesRetrieve(params.base_currency, params.currencies)
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesStableById
 *
 * Get only stablecoins.
 * 
 * GET /api/currencies/stable/
 *
 * @method GET
 * @path /cfg/payments/currencies/stable/
 */
export async function getCfgPaymentsCurrenciesStableById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesStableRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsCurrenciesStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/currencies/stats/
 */
export async function getCfgPaymentsCurrenciesStatsById(
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesStatsRetrieve()
  return CurrencySchema.parse(response)
}

/**
 * Get supported currencies
 *
 * Get list of supported currencies from payment providers
 *
 * @method GET
 * @path /cfg/payments/currencies/supported/
 */
export async function getCfgPaymentsCurrenciesSupportedById(
  params?: { currency_type?: string; provider?: string },
  client?: API
): Promise<Currency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsCurrenciesSupportedRetrieve(params?.currency_type, params?.provider)
  return CurrencySchema.parse(response)
}

/**
 * getCfgPaymentsEndpointGroupsList
 *
 * Endpoint Group ViewSet: /api/endpoint-groups/
 * 
 * Read-only access to endpoint group information.
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/
 */
export async function getCfgPaymentsEndpointGroupsList(
  params?: { is_enabled?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedEndpointGroupList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsEndpointGroupsList(params?.is_enabled, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedEndpointGroupListSchema.parse(response)
}

/**
 * getCfgPaymentsEndpointGroupsById
 *
 * Endpoint Group ViewSet: /api/endpoint-groups/
 * 
 * Read-only access to endpoint group information.
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/{id}/
 */
export async function getCfgPaymentsEndpointGroupsById(
  id: number,
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsEndpointGroupsRetrieve(id)
  return EndpointGroupSchema.parse(response)
}

/**
 * getCfgPaymentsEndpointGroupsAvailableById
 *
 * Get available endpoint groups for subscription.
 * 
 * GET /api/endpoint-groups/available/
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/available/
 */
export async function getCfgPaymentsEndpointGroupsAvailableById(
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsEndpointGroupsAvailableRetrieve()
  return EndpointGroupSchema.parse(response)
}

/**
 * getCfgPaymentsEndpointGroupsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/health/
 */
export async function getCfgPaymentsEndpointGroupsHealthById(
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsEndpointGroupsHealthRetrieve()
  return EndpointGroupSchema.parse(response)
}

/**
 * getCfgPaymentsEndpointGroupsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/endpoint-groups/stats/
 */
export async function getCfgPaymentsEndpointGroupsStatsById(
  client?: API
): Promise<EndpointGroup> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsEndpointGroupsStatsRetrieve()
  return EndpointGroupSchema.parse(response)
}

/**
 * getCfgPaymentsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/health/
 */
export async function getCfgPaymentsHealthById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsHealthRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsNetworksList
 *
 * Network ViewSet: /api/networks/
 * 
 * Read-only access to blockchain network information.
 *
 * @method GET
 * @path /cfg/payments/networks/
 */
export async function getCfgPaymentsNetworksList(
  params?: { is_active?: boolean; native_currency__code?: string; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedNetworkList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsNetworksList(params?.is_active, params?.native_currency__code, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedNetworkListSchema.parse(response)
}

/**
 * getCfgPaymentsNetworksById
 *
 * Network ViewSet: /api/networks/
 * 
 * Read-only access to blockchain network information.
 *
 * @method GET
 * @path /cfg/payments/networks/{id}/
 */
export async function getCfgPaymentsNetworksById(
  id: number,
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsNetworksRetrieve(id)
  return NetworkSchema.parse(response)
}

/**
 * getCfgPaymentsNetworksByCurrencyById
 *
 * Get networks grouped by currency.
 * 
 * GET /api/networks/by_currency/
 *
 * @method GET
 * @path /cfg/payments/networks/by_currency/
 */
export async function getCfgPaymentsNetworksByCurrencyById(
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsNetworksByCurrencyRetrieve()
  return NetworkSchema.parse(response)
}

/**
 * getCfgPaymentsNetworksHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/networks/health/
 */
export async function getCfgPaymentsNetworksHealthById(
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsNetworksHealthRetrieve()
  return NetworkSchema.parse(response)
}

/**
 * getCfgPaymentsNetworksStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/networks/stats/
 */
export async function getCfgPaymentsNetworksStatsById(
  client?: API
): Promise<Network> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsNetworksStatsRetrieve()
  return NetworkSchema.parse(response)
}

/**
 * API Keys Overview
 *
 * Get API keys overview
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/api_keys_overview/
 */
export async function getCfgPaymentsOverviewDashboardApiKeysOverviewById(
  client?: API
): Promise<APIKeysOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardApiKeysOverviewRetrieve()
  return APIKeysOverviewSchema.parse(response)
}

/**
 * Balance Overview
 *
 * Get user balance overview
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/balance_overview/
 */
export async function getCfgPaymentsOverviewDashboardBalanceOverviewById(
  client?: API
): Promise<BalanceOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardBalanceOverviewRetrieve()
  return BalanceOverviewSchema.parse(response)
}

/**
 * Payments Chart Data
 *
 * Get chart data for payments visualization
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/chart_data/
 */
export async function getCfgPaymentsOverviewDashboardChartDataById(
  params?: { period?: string },
  client?: API
): Promise<PaymentsChartResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardChartDataRetrieve(params?.period)
  return PaymentsChartResponseSchema.parse(response)
}

/**
 * Payments Dashboard Metrics
 *
 * Get payments dashboard metrics including balance, subscriptions, API keys, and payments
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/metrics/
 */
export async function getCfgPaymentsOverviewDashboardMetricsById(
  client?: API
): Promise<PaymentsMetrics> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardMetricsRetrieve()
  return PaymentsMetricsSchema.parse(response)
}

/**
 * Payments Dashboard Overview
 *
 * Get complete payments dashboard overview with metrics, recent payments, and analytics
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/overview/
 */
export async function getCfgPaymentsOverviewDashboardOverviewById(
  client?: API
): Promise<PaymentsDashboardOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardOverviewRetrieve()
  return PaymentsDashboardOverviewSchema.parse(response)
}

/**
 * Payment Analytics
 *
 * Get analytics for payments by currency and provider
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/payment_analytics/
 */
export async function getCfgPaymentsOverviewDashboardPaymentAnalyticsById(
  params?: { limit?: number },
  client?: API
): Promise<PaymentAnalyticsResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardPaymentAnalyticsRetrieve(params?.limit)
  return PaymentAnalyticsResponseSchema.parse(response)
}

/**
 * Recent Payments
 *
 * Get recent payments for the user
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/recent_payments/
 */
export async function getCfgPaymentsOverviewDashboardRecentPaymentsList(
  params?: { limit?: number; page?: number; page_size?: number },
  client?: API
): Promise<PaginatedRecentPaymentList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardRecentPaymentsList(params?.limit, params?.page, params?.page_size)
  return PaginatedRecentPaymentListSchema.parse(response)
}

/**
 * Recent Transactions
 *
 * Get recent balance transactions for the user
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/recent_transactions/
 */
export async function getCfgPaymentsOverviewDashboardRecentTransactionsList(
  params?: { limit?: number; page?: number; page_size?: number },
  client?: API
): Promise<PaginatedRecentTransactionList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardRecentTransactionsList(params?.limit, params?.page, params?.page_size)
  return PaginatedRecentTransactionListSchema.parse(response)
}

/**
 * Subscription Overview
 *
 * Get current subscription overview
 *
 * @method GET
 * @path /cfg/payments/overview/dashboard/subscription_overview/
 */
export async function getCfgPaymentsOverviewDashboardSubscriptionOverviewById(
  client?: API
): Promise<SubscriptionOverview> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsOverviewDashboardSubscriptionOverviewRetrieve()
  return SubscriptionOverviewSchema.parse(response)
}

/**
 * getCfgPaymentsPaymentsList
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method GET
 * @path /cfg/payments/payments/
 */
export async function getCfgPaymentsPaymentsList(
  params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string; user?: number },
  client?: API
): Promise<PaginatedPaymentListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsList(params?.currency__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search, params?.status, params?.user)
  return PaginatedPaymentListListSchema.parse(response)
}

/**
 * createCfgPaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method POST
 * @path /cfg/payments/payments/
 */
export async function createCfgPaymentsPayments(
  data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsCreate(data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getCfgPaymentsPaymentsById
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method GET
 * @path /cfg/payments/payments/{id}/
 */
export async function getCfgPaymentsPaymentsById(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsRetrieve(id)
  return PaymentSchema.parse(response)
}

/**
 * updateCfgPaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method PUT
 * @path /cfg/payments/payments/{id}/
 */
export async function updateCfgPaymentsPayments(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsUpdate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method PATCH
 * @path /cfg/payments/payments/{id}/
 */
export async function partialUpdateCfgPaymentsPayments(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsPartialUpdate(id)
  return PaymentSchema.parse(response)
}

/**
 * deleteCfgPaymentsPayments
 *
 * Global payment ViewSet: /api/v1/payments/
 * 
 * Provides admin-level access to all payments with filtering and stats.
 *
 * @method DELETE
 * @path /cfg/payments/payments/{id}/
 */
export async function deleteCfgPaymentsPayments(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsDestroy(id)
  return response
}

/**
 * createCfgPaymentsPaymentsCancel
 *
 * Cancel payment.
 * 
 * POST /api/v1/payments/{id}/cancel/
 *
 * @method POST
 * @path /cfg/payments/payments/{id}/cancel/
 */
export async function createCfgPaymentsPaymentsCancel(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsCancelCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * createCfgPaymentsPaymentsCheckStatus
 *
 * Check payment status with provider.
 * 
 * POST /api/v1/payments/{id}/check_status/
 *
 * @method POST
 * @path /cfg/payments/payments/{id}/check_status/
 */
export async function createCfgPaymentsPaymentsCheckStatus(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsCheckStatusCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsPaymentsAnalyticsById
 *
 * Get payment analytics.
 * 
 * GET /api/v1/payments/analytics/?days=30
 *
 * @method GET
 * @path /cfg/payments/payments/analytics/
 */
export async function getCfgPaymentsPaymentsAnalyticsById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsAnalyticsRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsPaymentsByProviderById
 *
 * Get payments grouped by provider.
 * 
 * GET /api/v1/payments/by_provider/
 *
 * @method GET
 * @path /cfg/payments/payments/by_provider/
 */
export async function getCfgPaymentsPaymentsByProviderById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsByProviderRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * createCfgPaymentsPaymentsCreate
 *
 * Standalone payment creation endpoint: /api/v1/payments/create/
 * 
 * Simplified endpoint for payment creation without full ViewSet overhead.
 *
 * @method POST
 * @path /cfg/payments/payments/create/
 */
export async function createCfgPaymentsPaymentsCreate(
  data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsCreateCreate(data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getCfgPaymentsPaymentsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/payments/health/
 */
export async function getCfgPaymentsPaymentsHealthById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsHealthRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsPaymentsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/payments/stats/
 */
export async function getCfgPaymentsPaymentsStatsById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsStatsRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsPaymentsStatusById
 *
 * Standalone payment status endpoint: /api/v1/payments/{id}/status/
 * 
 * Quick status check without full ViewSet overhead.
 *
 * @method GET
 * @path /cfg/payments/payments/status/{id}/
 */
export async function getCfgPaymentsPaymentsStatusById(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsPaymentsStatusRetrieve(id)
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsProviderCurrenciesList
 *
 * Provider Currency ViewSet: /api/provider-currencies/
 * 
 * Read-only access to provider-specific currency information.
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/
 */
export async function getCfgPaymentsProviderCurrenciesList(
  params?: { currency__code?: string; is_enabled?: boolean; network__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string },
  client?: API
): Promise<PaginatedProviderCurrencyList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsProviderCurrenciesList(params?.currency__code, params?.is_enabled, params?.network__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search)
  return PaginatedProviderCurrencyListSchema.parse(response)
}

/**
 * getCfgPaymentsProviderCurrenciesById
 *
 * Provider Currency ViewSet: /api/provider-currencies/
 * 
 * Read-only access to provider-specific currency information.
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/{id}/
 */
export async function getCfgPaymentsProviderCurrenciesById(
  id: number,
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsProviderCurrenciesRetrieve(id)
  return ProviderCurrencySchema.parse(response)
}

/**
 * getCfgPaymentsProviderCurrenciesByProviderById
 *
 * Get provider currencies grouped by provider.
 * 
 * GET /api/provider-currencies/by_provider/
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/by_provider/
 */
export async function getCfgPaymentsProviderCurrenciesByProviderById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsProviderCurrenciesByProviderRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getCfgPaymentsProviderCurrenciesHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/health/
 */
export async function getCfgPaymentsProviderCurrenciesHealthById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsProviderCurrenciesHealthRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getCfgPaymentsProviderCurrenciesLimitsById
 *
 * Get currency limits by provider.
 * 
 * GET /api/provider-currencies/limits/?provider=nowpayments
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/limits/
 */
export async function getCfgPaymentsProviderCurrenciesLimitsById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsProviderCurrenciesLimitsRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getCfgPaymentsProviderCurrenciesStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/provider-currencies/stats/
 */
export async function getCfgPaymentsProviderCurrenciesStatsById(
  client?: API
): Promise<ProviderCurrency> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsProviderCurrenciesStatsRetrieve()
  return ProviderCurrencySchema.parse(response)
}

/**
 * getCfgPaymentsSubscriptionsList
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method GET
 * @path /cfg/payments/subscriptions/
 */
export async function getCfgPaymentsSubscriptionsList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string; user?: number },
  client?: API
): Promise<PaginatedSubscriptionListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsList(params?.ordering, params?.page, params?.page_size, params?.search, params?.status, params?.tier, params?.user)
  return PaginatedSubscriptionListListSchema.parse(response)
}

/**
 * createCfgPaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method POST
 * @path /cfg/payments/subscriptions/
 */
export async function createCfgPaymentsSubscriptions(
  data: SubscriptionCreateRequest,
  client?: API
): Promise<SubscriptionCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsCreate(data)
  return SubscriptionCreateSchema.parse(response)
}

/**
 * getCfgPaymentsSubscriptionsById
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method GET
 * @path /cfg/payments/subscriptions/{id}/
 */
export async function getCfgPaymentsSubscriptionsById(
  id: string,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsRetrieve(id)
  return SubscriptionSchema.parse(response)
}

/**
 * updateCfgPaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method PUT
 * @path /cfg/payments/subscriptions/{id}/
 */
export async function updateCfgPaymentsSubscriptions(
  id: string, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsUpdate(id, data)
  return SubscriptionSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method PATCH
 * @path /cfg/payments/subscriptions/{id}/
 */
export async function partialUpdateCfgPaymentsSubscriptions(
  id: string,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsPartialUpdate(id)
  return SubscriptionSchema.parse(response)
}

/**
 * deleteCfgPaymentsSubscriptions
 *
 * Global subscription ViewSet: /api/subscriptions/
 * 
 * Provides admin-level access to all subscriptions with filtering and stats.
 *
 * @method DELETE
 * @path /cfg/payments/subscriptions/{id}/
 */
export async function deleteCfgPaymentsSubscriptions(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsDestroy(id)
  return response
}

/**
 * createCfgPaymentsSubscriptionsIncrementUsage
 *
 * Increment subscription usage.
 * 
 * POST /api/subscriptions/{id}/increment_usage/
 *
 * @method POST
 * @path /cfg/payments/subscriptions/{id}/increment_usage/
 */
export async function createCfgPaymentsSubscriptionsIncrementUsage(
  id: string, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsIncrementUsageCreate(id, data)
  return SubscriptionSchema.parse(response)
}

/**
 * createCfgPaymentsSubscriptionsUpdateStatus
 *
 * Update subscription status.
 * 
 * POST /api/subscriptions/{id}/update_status/
 *
 * @method POST
 * @path /cfg/payments/subscriptions/{id}/update_status/
 */
export async function createCfgPaymentsSubscriptionsUpdateStatus(
  id: string, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsUpdateStatusCreate(id, data)
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsSubscriptionsAnalyticsById
 *
 * Get subscription analytics.
 * 
 * GET /api/subscriptions/analytics/?days=30
 *
 * @method GET
 * @path /cfg/payments/subscriptions/analytics/
 */
export async function getCfgPaymentsSubscriptionsAnalyticsById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsAnalyticsRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsSubscriptionsByStatusById
 *
 * Get subscriptions grouped by status.
 * 
 * GET /api/subscriptions/by_status/
 *
 * @method GET
 * @path /cfg/payments/subscriptions/by_status/
 */
export async function getCfgPaymentsSubscriptionsByStatusById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsByStatusRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsSubscriptionsByTierById
 *
 * Get subscriptions grouped by tier.
 * 
 * GET /api/subscriptions/by_tier/
 *
 * @method GET
 * @path /cfg/payments/subscriptions/by_tier/
 */
export async function getCfgPaymentsSubscriptionsByTierById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsByTierRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsSubscriptionsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/subscriptions/health/
 */
export async function getCfgPaymentsSubscriptionsHealthById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsHealthRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsSubscriptionsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/subscriptions/stats/
 */
export async function getCfgPaymentsSubscriptionsStatsById(
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsSubscriptionsStatsRetrieve()
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsTariffsList
 *
 * Tariff ViewSet: /api/tariffs/
 * 
 * Read-only access to tariff information for subscription selection.
 *
 * @method GET
 * @path /cfg/payments/tariffs/
 */
export async function getCfgPaymentsTariffsList(
  params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedTariffList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTariffsList(params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedTariffListSchema.parse(response)
}

/**
 * getCfgPaymentsTariffsById
 *
 * Tariff ViewSet: /api/tariffs/
 * 
 * Read-only access to tariff information for subscription selection.
 *
 * @method GET
 * @path /cfg/payments/tariffs/{id}/
 */
export async function getCfgPaymentsTariffsById(
  id: number,
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTariffsRetrieve(id)
  return TariffSchema.parse(response)
}

/**
 * getCfgPaymentsTariffsEndpointGroupsById
 *
 * Get endpoint groups for specific tariff.
 * 
 * GET /api/tariffs/{id}/endpoint_groups/
 *
 * @method GET
 * @path /cfg/payments/tariffs/{id}/endpoint_groups/
 */
export async function getCfgPaymentsTariffsEndpointGroupsById(
  id: number,
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTariffsEndpointGroupsRetrieve(id)
  return TariffSchema.parse(response)
}

/**
 * getCfgPaymentsTariffsFreeById
 *
 * Get free tariffs.
 * 
 * GET /api/tariffs/free/
 *
 * @method GET
 * @path /cfg/payments/tariffs/free/
 */
export async function getCfgPaymentsTariffsFreeById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTariffsFreeRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getCfgPaymentsTariffsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/tariffs/health/
 */
export async function getCfgPaymentsTariffsHealthById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTariffsHealthRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getCfgPaymentsTariffsPaidById
 *
 * Get paid tariffs.
 * 
 * GET /api/tariffs/paid/
 *
 * @method GET
 * @path /cfg/payments/tariffs/paid/
 */
export async function getCfgPaymentsTariffsPaidById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTariffsPaidRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getCfgPaymentsTariffsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/tariffs/stats/
 */
export async function getCfgPaymentsTariffsStatsById(
  client?: API
): Promise<Tariff> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTariffsStatsRetrieve()
  return TariffSchema.parse(response)
}

/**
 * getCfgPaymentsTransactionsList
 *
 * Transaction ViewSet: /api/transactions/
 * 
 * Read-only access to transaction history with filtering.
 *
 * @method GET
 * @path /cfg/payments/transactions/
 */
export async function getCfgPaymentsTransactionsList(
  params?: { ordering?: string; page?: number; page_size?: number; payment_id?: string; search?: string; transaction_type?: string; user?: number },
  client?: API
): Promise<PaginatedTransactionList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTransactionsList(params?.ordering, params?.page, params?.page_size, params?.payment_id, params?.search, params?.transaction_type, params?.user)
  return PaginatedTransactionListSchema.parse(response)
}

/**
 * getCfgPaymentsTransactionsById
 *
 * Transaction ViewSet: /api/transactions/
 * 
 * Read-only access to transaction history with filtering.
 *
 * @method GET
 * @path /cfg/payments/transactions/{id}/
 */
export async function getCfgPaymentsTransactionsById(
  id: string,
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTransactionsRetrieve(id)
  return TransactionSchema.parse(response)
}

/**
 * getCfgPaymentsTransactionsByTypeById
 *
 * Get transactions grouped by type.
 * 
 * GET /api/transactions/by_type/
 *
 * @method GET
 * @path /cfg/payments/transactions/by_type/
 */
export async function getCfgPaymentsTransactionsByTypeById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTransactionsByTypeRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getCfgPaymentsTransactionsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/transactions/health/
 */
export async function getCfgPaymentsTransactionsHealthById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTransactionsHealthRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getCfgPaymentsTransactionsRecentById
 *
 * Get recent transactions.
 * 
 * GET /api/transactions/recent/?limit=10
 *
 * @method GET
 * @path /cfg/payments/transactions/recent/
 */
export async function getCfgPaymentsTransactionsRecentById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTransactionsRecentRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getCfgPaymentsTransactionsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/transactions/stats/
 */
export async function getCfgPaymentsTransactionsStatsById(
  client?: API
): Promise<Transaction> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsTransactionsStatsRetrieve()
  return TransactionSchema.parse(response)
}

/**
 * getCfgPaymentsUsersList
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/
 */
export async function getCfgPaymentsUsersList(
  params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string },
  client?: API
): Promise<PaginatedPaymentListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersList(params?.currency__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search, params?.status)
  return PaginatedPaymentListListSchema.parse(response)
}

/**
 * createCfgPaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method POST
 * @path /cfg/payments/users/
 */
export async function createCfgPaymentsUsers(
  data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersCreate(data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getCfgPaymentsUsersById
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/{id}/
 */
export async function getCfgPaymentsUsersById(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersRetrieve(id)
  return PaymentSchema.parse(response)
}

/**
 * updateCfgPaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PUT
 * @path /cfg/payments/users/{id}/
 */
export async function updateCfgPaymentsUsers(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersUpdate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PATCH
 * @path /cfg/payments/users/{id}/
 */
export async function partialUpdateCfgPaymentsUsers(
  id: string,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPartialUpdate(id)
  return PaymentSchema.parse(response)
}

/**
 * deleteCfgPaymentsUsers
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method DELETE
 * @path /cfg/payments/users/{id}/
 */
export async function deleteCfgPaymentsUsers(
  id: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersDestroy(id)
  return response
}

/**
 * createCfgPaymentsUsersCancel
 *
 * Cancel payment.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/cancel/
 *
 * @method POST
 * @path /cfg/payments/users/{id}/cancel/
 */
export async function createCfgPaymentsUsersCancel(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersCancelCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * createCfgPaymentsUsersCheckStatus
 *
 * Check payment status with provider.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/check_status/
 *
 * @method POST
 * @path /cfg/payments/users/{id}/check_status/
 */
export async function createCfgPaymentsUsersCheckStatus(
  id: string, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersCheckStatusCreate(id, data)
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsUsersApiKeysList
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/
 */
export async function getCfgPaymentsUsersApiKeysList(
  user_pk: number, params?: { is_active?: boolean; ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedAPIKeyListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysList(user_pk, params?.is_active, params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedAPIKeyListListSchema.parse(response)
}

/**
 * createCfgPaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/api-keys/
 */
export async function createCfgPaymentsUsersApiKeys(
  user_pk: number, data: APIKeyCreateRequest,
  client?: API
): Promise<APIKeyCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysCreate(user_pk, data)
  return APIKeyCreateSchema.parse(response)
}

/**
 * getCfgPaymentsUsersApiKeysById
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export async function getCfgPaymentsUsersApiKeysById(
  id: string, user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysRetrieve(id, user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * updateCfgPaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method PUT
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export async function updateCfgPaymentsUsersApiKeys(
  id: string, user_pk: number, data: APIKeyUpdateRequest,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysUpdate(id, user_pk, data)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method PATCH
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export async function partialUpdateCfgPaymentsUsersApiKeys(
  id: string, user_pk: number,
  client?: API
): Promise<APIKeyUpdate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysPartialUpdate(id, user_pk)
  return APIKeyUpdateSchema.parse(response)
}

/**
 * deleteCfgPaymentsUsersApiKeys
 *
 * User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
 * 
 * Provides user-scoped access to API keys with full CRUD operations.
 *
 * @method DELETE
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/
 */
export async function deleteCfgPaymentsUsersApiKeys(
  id: string, user_pk: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysDestroy(id, user_pk)
  return response
}

/**
 * createCfgPaymentsUsersApiKeysPerformAction
 *
 * Perform action on API key.
 * 
 * POST /api/users/{user_id}/api-keys/{id}/perform_action/
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/api-keys/{id}/perform_action/
 */
export async function createCfgPaymentsUsersApiKeysPerformAction(
  id: string, user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysPerformActionCreate(id, user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsUsersApiKeysActiveById
 *
 * Get user's active API keys.
 * 
 * GET /api/users/{user_id}/api-keys/active/
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/active/
 */
export async function getCfgPaymentsUsersApiKeysActiveById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysActiveRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsUsersApiKeysHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/health/
 */
export async function getCfgPaymentsUsersApiKeysHealthById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysHealthRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsUsersApiKeysStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/stats/
 */
export async function getCfgPaymentsUsersApiKeysStatsById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysStatsRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsUsersApiKeysSummaryById
 *
 * Get user API key summary.
 * 
 * GET /api/users/{user_id}/api-keys/summary/
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/api-keys/summary/
 */
export async function getCfgPaymentsUsersApiKeysSummaryById(
  user_pk: number,
  client?: API
): Promise<APIKeyDetail> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersApiKeysSummaryRetrieve(user_pk)
  return APIKeyDetailSchema.parse(response)
}

/**
 * getCfgPaymentsUsersPaymentsList
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/
 */
export async function getCfgPaymentsUsersPaymentsList(
  user_pk: number, params?: { currency__code?: string; ordering?: string; page?: number; page_size?: number; provider?: string; search?: string; status?: string },
  client?: API
): Promise<PaginatedPaymentListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsList(user_pk, params?.currency__code, params?.ordering, params?.page, params?.page_size, params?.provider, params?.search, params?.status)
  return PaginatedPaymentListListSchema.parse(response)
}

/**
 * createCfgPaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/payments/
 */
export async function createCfgPaymentsUsersPayments(
  user_pk: number, data: PaymentCreateRequest,
  client?: API
): Promise<PaymentCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsCreate(user_pk, data)
  return PaymentCreateSchema.parse(response)
}

/**
 * getCfgPaymentsUsersPaymentsById
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export async function getCfgPaymentsUsersPaymentsById(
  id: string, user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsRetrieve(id, user_pk)
  return PaymentSchema.parse(response)
}

/**
 * updateCfgPaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PUT
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export async function updateCfgPaymentsUsersPayments(
  id: string, user_pk: number, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsUpdate(id, user_pk, data)
  return PaymentSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method PATCH
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export async function partialUpdateCfgPaymentsUsersPayments(
  id: string, user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsPartialUpdate(id, user_pk)
  return PaymentSchema.parse(response)
}

/**
 * deleteCfgPaymentsUsersPayments
 *
 * User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
 * 
 * Provides user-scoped access to payments with full CRUD operations.
 *
 * @method DELETE
 * @path /cfg/payments/users/{user_pk}/payments/{id}/
 */
export async function deleteCfgPaymentsUsersPayments(
  id: string, user_pk: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsDestroy(id, user_pk)
  return response
}

/**
 * createCfgPaymentsUsersPaymentsCancel
 *
 * Cancel payment.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/cancel/
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/payments/{id}/cancel/
 */
export async function createCfgPaymentsUsersPaymentsCancel(
  id: string, user_pk: number, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsCancelCreate(id, user_pk, data)
  return PaymentSchema.parse(response)
}

/**
 * createCfgPaymentsUsersPaymentsCheckStatus
 *
 * Check payment status with provider.
 * 
 * POST /api/v1/users/{user_id}/payments/{id}/check_status/
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/payments/{id}/check_status/
 */
export async function createCfgPaymentsUsersPaymentsCheckStatus(
  id: string, user_pk: number, data: PaymentRequest,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsCheckStatusCreate(id, user_pk, data)
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsUsersPaymentsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/health/
 */
export async function getCfgPaymentsUsersPaymentsHealthById(
  user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsHealthRetrieve(user_pk)
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsUsersPaymentsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/stats/
 */
export async function getCfgPaymentsUsersPaymentsStatsById(
  user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsStatsRetrieve(user_pk)
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsUsersPaymentsSummaryById
 *
 * Get user payment summary.
 * 
 * GET /api/v1/users/{user_id}/payments/summary/
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/payments/summary/
 */
export async function getCfgPaymentsUsersPaymentsSummaryById(
  user_pk: number,
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersPaymentsSummaryRetrieve(user_pk)
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsUsersSubscriptionsList
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/
 */
export async function getCfgPaymentsUsersSubscriptionsList(
  user_pk: number, params?: { ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tier?: string },
  client?: API
): Promise<PaginatedSubscriptionListList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsList(user_pk, params?.ordering, params?.page, params?.page_size, params?.search, params?.status, params?.tier)
  return PaginatedSubscriptionListListSchema.parse(response)
}

/**
 * createCfgPaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/subscriptions/
 */
export async function createCfgPaymentsUsersSubscriptions(
  user_pk: number, data: SubscriptionCreateRequest,
  client?: API
): Promise<SubscriptionCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsCreate(user_pk, data)
  return SubscriptionCreateSchema.parse(response)
}

/**
 * getCfgPaymentsUsersSubscriptionsById
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export async function getCfgPaymentsUsersSubscriptionsById(
  id: string, user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsRetrieve(id, user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * updateCfgPaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method PUT
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export async function updateCfgPaymentsUsersSubscriptions(
  id: string, user_pk: number, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsUpdate(id, user_pk, data)
  return SubscriptionSchema.parse(response)
}

/**
 * partialUpdateCfgPaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method PATCH
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export async function partialUpdateCfgPaymentsUsersSubscriptions(
  id: string, user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsPartialUpdate(id, user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * deleteCfgPaymentsUsersSubscriptions
 *
 * User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
 * 
 * Provides user-scoped access to subscriptions with full CRUD operations.
 *
 * @method DELETE
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/
 */
export async function deleteCfgPaymentsUsersSubscriptions(
  id: string, user_pk: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsDestroy(id, user_pk)
  return response
}

/**
 * createCfgPaymentsUsersSubscriptionsIncrementUsage
 *
 * Increment subscription usage.
 * 
 * POST /api/users/{user_id}/subscriptions/{id}/increment_usage/
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/increment_usage/
 */
export async function createCfgPaymentsUsersSubscriptionsIncrementUsage(
  id: string, user_pk: number, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsIncrementUsageCreate(id, user_pk, data)
  return SubscriptionSchema.parse(response)
}

/**
 * createCfgPaymentsUsersSubscriptionsUpdateStatus
 *
 * Update subscription status.
 * 
 * POST /api/users/{user_id}/subscriptions/{id}/update_status/
 *
 * @method POST
 * @path /cfg/payments/users/{user_pk}/subscriptions/{id}/update_status/
 */
export async function createCfgPaymentsUsersSubscriptionsUpdateStatus(
  id: string, user_pk: number, data: SubscriptionRequest,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsUpdateStatusCreate(id, user_pk, data)
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsUsersSubscriptionsActiveById
 *
 * Get user's active subscription.
 * 
 * GET /api/users/{user_id}/subscriptions/active/
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/active/
 */
export async function getCfgPaymentsUsersSubscriptionsActiveById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsActiveRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsUsersSubscriptionsHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/health/
 */
export async function getCfgPaymentsUsersSubscriptionsHealthById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsHealthRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsUsersSubscriptionsStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/stats/
 */
export async function getCfgPaymentsUsersSubscriptionsStatsById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsStatsRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsUsersSubscriptionsSummaryById
 *
 * Get user subscription summary.
 * 
 * GET /api/users/{user_id}/subscriptions/summary/
 *
 * @method GET
 * @path /cfg/payments/users/{user_pk}/subscriptions/summary/
 */
export async function getCfgPaymentsUsersSubscriptionsSummaryById(
  user_pk: number,
  client?: API
): Promise<Subscription> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSubscriptionsSummaryRetrieve(user_pk)
  return SubscriptionSchema.parse(response)
}

/**
 * getCfgPaymentsUsersHealthById
 *
 * Health check for the ViewSet and related services.
 * 
 * Returns service status and basic metrics.
 *
 * @method GET
 * @path /cfg/payments/users/health/
 */
export async function getCfgPaymentsUsersHealthById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersHealthRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsUsersStatsById
 *
 * Get statistics for the current queryset.
 * 
 * Returns counts, aggregates, and breakdowns.
 *
 * @method GET
 * @path /cfg/payments/users/stats/
 */
export async function getCfgPaymentsUsersStatsById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersStatsRetrieve()
  return PaymentSchema.parse(response)
}

/**
 * getCfgPaymentsUsersSummaryById
 *
 * Get user payment summary.
 * 
 * GET /api/v1/users/{user_id}/payments/summary/
 *
 * @method GET
 * @path /cfg/payments/users/summary/
 */
export async function getCfgPaymentsUsersSummaryById(
  client?: API
): Promise<Payment> {
  const api = client || getAPIInstance()

  const response = await api.cfg__payments.cfgPaymentsUsersSummaryRetrieve()
  return PaymentSchema.parse(response)
}

