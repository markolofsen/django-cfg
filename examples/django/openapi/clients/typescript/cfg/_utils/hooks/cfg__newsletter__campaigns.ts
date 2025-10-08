/**
 * SWR Hooks for Campaigns
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
import type { NewsletterCampaignRequest } from '../schemas/NewsletterCampaignRequest.schema'
import type { PaginatedNewsletterCampaignList } from '../schemas/PaginatedNewsletterCampaignList.schema'
import type { SendCampaignRequest } from '../schemas/SendCampaignRequest.schema'
import type { SendCampaignResponse } from '../schemas/SendCampaignResponse.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List Newsletter Campaigns
 *
 * @method GET
 * @path /django_cfg_newsletter/campaigns/
 */
export function useDjangoCfgNewsletterCampaignsList(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedNewsletterCampaignList>(
    params ? ['django-cfg-newsletter-campaigns', params] : 'django-cfg-newsletter-campaigns',
    () => Fetchers.getDjangoCfgNewsletterCampaignsList(params)
  )
}

/**
 * Get Campaign Details
 *
 * @method GET
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export function useDjangoCfgNewsletterCampaignsById(id: number) {
  return useSWR<NewsletterCampaign>(
    ['django-cfg-newsletter-campaign', id],
    () => Fetchers.getDjangoCfgNewsletterCampaignsById(id)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Create Newsletter Campaign
 *
 * @method POST
 * @path /django_cfg_newsletter/campaigns/
 */
export function useCreateDjangoCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (data: NewsletterCampaignRequest): Promise<NewsletterCampaign> => {
    const result = await Fetchers.createDjangoCfgNewsletterCampaigns(data)

    // Revalidate related queries
    mutate('django-cfg-newsletter-campaigns')

    return result
  }
}

/**
 * Update Campaign
 *
 * @method PUT
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export function useUpdateDjangoCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: NewsletterCampaignRequest): Promise<NewsletterCampaign> => {
    const result = await Fetchers.updateDjangoCfgNewsletterCampaigns(id, data)

    // Revalidate related queries
    mutate('django-cfg-newsletter-campaigns')
    mutate('django-cfg-newsletter-campaign')

    return result
  }
}

/**
 * Delete Campaign
 *
 * @method DELETE
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export function useDeleteDjangoCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<void> => {
    const result = await Fetchers.deleteDjangoCfgNewsletterCampaigns(id)

    // Revalidate related queries
    mutate('django-cfg-newsletter-campaigns')
    mutate('django-cfg-newsletter-campaign')

    return result
  }
}

/**
 * Send Newsletter Campaign
 *
 * @method POST
 * @path /django_cfg_newsletter/campaigns/send/
 */
export function useCreateDjangoCfgNewsletterCampaignsSend() {
  const { mutate } = useSWRConfig()

  return async (data: SendCampaignRequest): Promise<SendCampaignResponse> => {
    const result = await Fetchers.createDjangoCfgNewsletterCampaignsSend(data)

    // Revalidate related queries
    mutate('django-cfg-newsletter-campaigns-send')

    return result
  }
}
