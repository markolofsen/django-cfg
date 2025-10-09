/**
 * SWR Hooks for Cfg Newsletter
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
import type { NewsletterCampaign } from '../schemas/NewsletterCampaign.schema'
import type { PatchedNewsletterCampaignRequest } from '../schemas/PatchedNewsletterCampaignRequest.schema'
import type { PatchedUnsubscribeRequest } from '../schemas/PatchedUnsubscribeRequest.schema'
import type { Unsubscribe } from '../schemas/Unsubscribe.schema'
import type { UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method PATCH
 * @path /cfg/newsletter/campaigns/{id}/
 */
export function usePartialUpdateCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<NewsletterCampaign> => {
    const result = await Fetchers.partialUpdateCfgNewsletterCampaigns(id)

    // Revalidate related queries
    mutate('cfg-newsletter-campaigns-partial')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/newsletter/unsubscribe/
 */
export function useUpdateCfgNewsletterUnsubscribe() {
  const { mutate } = useSWRConfig()

  return async (data: UnsubscribeRequest): Promise<Unsubscribe> => {
    const result = await Fetchers.updateCfgNewsletterUnsubscribe(data)

    // Revalidate related queries
    mutate('cfg-newsletter-unsubscribe')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/newsletter/unsubscribe/
 */
export function usePartialUpdateCfgNewsletterUnsubscribe() {
  const { mutate } = useSWRConfig()

  return async (): Promise<Unsubscribe> => {
    const result = await Fetchers.partialUpdateCfgNewsletterUnsubscribe()

    // Revalidate related queries
    mutate('cfg-newsletter-unsubscribe-partial')

    return result
  }
}
