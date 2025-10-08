/**
 * Typed fetchers for Webhooks
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
import { SupportedProvidersSchema, type SupportedProviders } from '../schemas/SupportedProviders.schema'
import { WebhookHealthSchema, type WebhookHealth } from '../schemas/WebhookHealth.schema'
import { WebhookResponseSchema, type WebhookResponse } from '../schemas/WebhookResponse.schema'
import { WebhookResponseRequestSchema, type WebhookResponseRequest } from '../schemas/WebhookResponseRequest.schema'
import { WebhookStatsSchema, type WebhookStats } from '../schemas/WebhookStats.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Webhook Endpoint Info
 *
 * Get webhook endpoint information for debugging and configuration
 *
 * @method GET
 * @path /payments/webhooks/{provider}/
 */
export async function getPaymentsWebhooksById(
  provider: string,
  client?: API
): Promise<WebhookResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_webhooks.paymentsWebhooksRetrieve(provider)
  return WebhookResponseSchema.parse(response)
}

/**
 * Process Webhook
 *
 * Process incoming webhook from payment provider
 *
 * @method POST
 * @path /payments/webhooks/{provider}/
 */
export async function createPaymentsWebhooks(
  provider: string, data: WebhookResponseRequest,
  client?: API
): Promise<WebhookResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_webhooks.paymentsWebhooksCreate(provider, data)
  return WebhookResponseSchema.parse(response)
}

/**
 * Webhook Health Check
 *
 * Check webhook service health status and recent activity metrics
 *
 * @method GET
 * @path /payments/webhooks/health/
 */
export async function getPaymentsWebhooksHealthById(
  client?: API
): Promise<WebhookHealth> {
  const api = client || getAPIInstance()

  const response = await api.cfg_webhooks.paymentsWebhooksHealthRetrieve()
  return WebhookHealthSchema.parse(response)
}

/**
 * Supported Webhook Providers
 *
 * Get list of supported webhook providers with configuration details
 *
 * @method GET
 * @path /payments/webhooks/providers/
 */
export async function getPaymentsWebhooksProvidersById(
  client?: API
): Promise<SupportedProviders> {
  const api = client || getAPIInstance()

  const response = await api.cfg_webhooks.paymentsWebhooksProvidersRetrieve()
  return SupportedProvidersSchema.parse(response)
}

/**
 * Webhook Statistics
 *
 * Get webhook processing statistics for a given time period
 *
 * @method GET
 * @path /payments/webhooks/stats/
 */
export async function getPaymentsWebhooksStatsById(
  params?: { days?: number },
  client?: API
): Promise<WebhookStats> {
  const api = client || getAPIInstance()

  const response = await api.cfg_webhooks.paymentsWebhooksStatsRetrieve(params?.days)
  return WebhookStatsSchema.parse(response)
}

