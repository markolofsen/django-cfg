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
 * @path /payments/webhooks/{provider}/
 */
export function usePaymentsWebhook(provider: string) {
  return useSWR<WebhookResponse>(
    ['payments-webhook', provider],
    () => Fetchers.getPaymentsWebhook(provider)
  )
}

/**
 * Webhook Health Check
 *
 * @method GET
 * @path /payments/webhooks/health/
 */
export function usePaymentsWebhooksHealth() {
  return useSWR<WebhookHealth>(
    'payments-webhooks-health',
    () => Fetchers.getPaymentsWebhooksHealth()
  )
}

/**
 * Supported Webhook Providers
 *
 * @method GET
 * @path /payments/webhooks/providers/
 */
export function usePaymentsWebhooksProvider() {
  return useSWR<SupportedProviders>(
    'payments-webhooks-provider',
    () => Fetchers.getPaymentsWebhooksProvider()
  )
}

/**
 * Webhook Statistics
 *
 * @method GET
 * @path /payments/webhooks/stats/
 */
export function usePaymentsWebhooksStat(params?: { days?: number }) {
  return useSWR<WebhookStats>(
    params ? ['payments-webhooks-stat', params] : 'payments-webhooks-stat',
    () => Fetchers.getPaymentsWebhooksStat(params)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Process Webhook
 *
 * @method POST
 * @path /payments/webhooks/{provider}/
 */
export function useCreatePaymentsWebhooks() {
  const { mutate } = useSWRConfig()

  return async (provider: string, data: WebhookResponseRequest): Promise<WebhookResponse> => {
    const result = await Fetchers.createPaymentsWebhooks(provider, data)

    // Revalidate related queries
    mutate('payments-webhooks')

    return result
  }
}
