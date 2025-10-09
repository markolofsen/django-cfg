/**
 * SWR Hooks for Webhooks
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
import type { SupportedProviders } from '../schemas/SupportedProviders.schema'
import type { WebhookHealth } from '../schemas/WebhookHealth.schema'
import type { WebhookResponse } from '../schemas/WebhookResponse.schema'
import type { WebhookResponseRequest } from '../schemas/WebhookResponseRequest.schema'
import type { WebhookStats } from '../schemas/WebhookStats.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * Webhook Endpoint Info
 *
 * @method GET
 * @path /cfg/payments/webhooks/{provider}/
 */
export function useCfgPaymentsWebhooksById(provider: string) {
  return useSWR<WebhookResponse>(
    ['cfg-payments-webhook', provider],
    () => Fetchers.getCfgPaymentsWebhooksById(provider)
  )
}

/**
 * Webhook Health Check
 *
 * @method GET
 * @path /cfg/payments/webhooks/health/
 */
export function useCfgPaymentsWebhooksHealthById() {
  return useSWR<WebhookHealth>(
    'cfg-payments-webhooks-health',
    () => Fetchers.getCfgPaymentsWebhooksHealthById()
  )
}

/**
 * Supported Webhook Providers
 *
 * @method GET
 * @path /cfg/payments/webhooks/providers/
 */
export function useCfgPaymentsWebhooksProvidersById() {
  return useSWR<SupportedProviders>(
    'cfg-payments-webhooks-provider',
    () => Fetchers.getCfgPaymentsWebhooksProvidersById()
  )
}

/**
 * Webhook Statistics
 *
 * @method GET
 * @path /cfg/payments/webhooks/stats/
 */
export function useCfgPaymentsWebhooksStatsById(params?: { days?: number }) {
  return useSWR<WebhookStats>(
    params ? ['cfg-payments-webhooks-stat', params] : 'cfg-payments-webhooks-stat',
    () => Fetchers.getCfgPaymentsWebhooksStatsById(params)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Process Webhook
 *
 * @method POST
 * @path /cfg/payments/webhooks/{provider}/
 */
export function useCreateCfgPaymentsWebhooks() {
  const { mutate } = useSWRConfig()

  return async (provider: string, data: WebhookResponseRequest): Promise<WebhookResponse> => {
    const result = await Fetchers.createCfgPaymentsWebhooks(provider, data)

    // Revalidate related queries
    mutate('cfg-payments-webhooks')

    return result
  }
}
