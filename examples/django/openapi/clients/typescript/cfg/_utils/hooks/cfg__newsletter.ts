/**
 * SWR Hooks for Newsletter
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
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export function usePartialUpdateDjangoCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<NewsletterCampaign> => {
    const result = await Fetchers.partialUpdateDjangoCfgNewsletterCampaigns(id)

    // Revalidate related queries
    mutate('django-cfg-newsletter-campaigns-partial')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /django_cfg_newsletter/unsubscribe/
 */
export function useUpdateDjangoCfgNewsletterUnsubscribe() {
  const { mutate } = useSWRConfig()

  return async (data: UnsubscribeRequest): Promise<Unsubscribe> => {
    const result = await Fetchers.updateDjangoCfgNewsletterUnsubscribe(data)

    // Revalidate related queries
    mutate('django-cfg-newsletter-unsubscribe')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /django_cfg_newsletter/unsubscribe/
 */
export function usePartialUpdateDjangoCfgNewsletterUnsubscribe() {
  const { mutate } = useSWRConfig()

  return async (): Promise<Unsubscribe> => {
    const result = await Fetchers.partialUpdateDjangoCfgNewsletterUnsubscribe()

    // Revalidate related queries
    mutate('django-cfg-newsletter-unsubscribe-partial')

    return result
  }
}
