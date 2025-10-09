/**
 * SWR Hooks for Subscriptions
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
import type { PaginatedNewsletterSubscriptionList } from '../schemas/PaginatedNewsletterSubscriptionList.schema'
import type { SubscribeRequest } from '../schemas/SubscribeRequest.schema'
import type { SubscribeResponse } from '../schemas/SubscribeResponse.schema'
import type { SuccessResponse } from '../schemas/SuccessResponse.schema'
import type { UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List User Subscriptions
 *
 * @method GET
 * @path /cfg/newsletter/subscriptions/
 */
export function useCfgNewsletterSubscriptionsList(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedNewsletterSubscriptionList>(
    params ? ['cfg-newsletter-subscriptions', params] : 'cfg-newsletter-subscriptions',
    () => Fetchers.getCfgNewsletterSubscriptionsList(params)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Subscribe to Newsletter
 *
 * @method POST
 * @path /cfg/newsletter/subscribe/
 */
export function useCreateCfgNewsletterSubscribe() {
  const { mutate } = useSWRConfig()

  return async (data: SubscribeRequest): Promise<SubscribeResponse> => {
    const result = await Fetchers.createCfgNewsletterSubscribe(data)

    // Revalidate related queries
    mutate('cfg-newsletter-subscribe')

    return result
  }
}

/**
 * Unsubscribe from Newsletter
 *
 * @method POST
 * @path /cfg/newsletter/unsubscribe/
 */
export function useCreateCfgNewsletterUnsubscribe() {
  const { mutate } = useSWRConfig()

  return async (data: UnsubscribeRequest): Promise<SuccessResponse> => {
    const result = await Fetchers.createCfgNewsletterUnsubscribe(data)

    // Revalidate related queries
    mutate('cfg-newsletter-unsubscribe')

    return result
  }
}
