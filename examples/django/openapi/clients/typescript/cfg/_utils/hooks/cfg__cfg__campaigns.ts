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
 * @path /cfg/newsletter/campaigns/
 */
export function useCfgNewsletterCampaignsList(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedNewsletterCampaignList>(
    params ? ['cfg-newsletter-campaigns', params] : 'cfg-newsletter-campaigns',
    () => Fetchers.getCfgNewsletterCampaignsList(params)
  )
}

/**
 * Get Campaign Details
 *
 * @method GET
 * @path /cfg/newsletter/campaigns/{id}/
 */
export function useCfgNewsletterCampaignsById(id: number) {
  return useSWR<NewsletterCampaign>(
    ['cfg-newsletter-campaign', id],
    () => Fetchers.getCfgNewsletterCampaignsById(id)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Create Newsletter Campaign
 *
 * @method POST
 * @path /cfg/newsletter/campaigns/
 */
export function useCreateCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (data: NewsletterCampaignRequest): Promise<NewsletterCampaign> => {
    const result = await Fetchers.createCfgNewsletterCampaigns(data)

    // Revalidate related queries
    mutate('cfg-newsletter-campaigns')

    return result
  }
}

/**
 * Update Campaign
 *
 * @method PUT
 * @path /cfg/newsletter/campaigns/{id}/
 */
export function useUpdateCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: NewsletterCampaignRequest): Promise<NewsletterCampaign> => {
    const result = await Fetchers.updateCfgNewsletterCampaigns(id, data)

    // Revalidate related queries
    mutate('cfg-newsletter-campaigns')
    mutate('cfg-newsletter-campaign')

    return result
  }
}

/**
 * Delete Campaign
 *
 * @method DELETE
 * @path /cfg/newsletter/campaigns/{id}/
 */
export function useDeleteCfgNewsletterCampaigns() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<void> => {
    const result = await Fetchers.deleteCfgNewsletterCampaigns(id)

    // Revalidate related queries
    mutate('cfg-newsletter-campaigns')
    mutate('cfg-newsletter-campaign')

    return result
  }
}

/**
 * Send Newsletter Campaign
 *
 * @method POST
 * @path /cfg/newsletter/campaigns/send/
 */
export function useCreateCfgNewsletterCampaignsSend() {
  const { mutate } = useSWRConfig()

  return async (data: SendCampaignRequest): Promise<SendCampaignResponse> => {
    const result = await Fetchers.createCfgNewsletterCampaignsSend(data)

    // Revalidate related queries
    mutate('cfg-newsletter-campaigns-send')

    return result
  }
}
