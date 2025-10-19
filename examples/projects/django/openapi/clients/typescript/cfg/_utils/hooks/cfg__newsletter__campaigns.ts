/**
 * SWR Hooks for Campaigns
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__newsletter__campaigns'
import type { API } from '../../index'
import type { NewsletterCampaign } from '../schemas/NewsletterCampaign.schema'
import type { NewsletterCampaignRequest } from '../schemas/NewsletterCampaignRequest.schema'
import type { PaginatedNewsletterCampaignList } from '../schemas/PaginatedNewsletterCampaignList.schema'
import type { SendCampaignRequest } from '../schemas/SendCampaignRequest.schema'
import type { SendCampaignResponse } from '../schemas/SendCampaignResponse.schema'

/**
 * List Newsletter Campaigns
 *
 * @method GET
 * @path /cfg/newsletter/campaigns/
 */
export function useNewsletterCampaignsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedNewsletterCampaignList>> {
  return useSWR<PaginatedNewsletterCampaignList>(
    params ? ['cfg-newsletter-campaigns', params] : 'cfg-newsletter-campaigns',
    () => Fetchers.getNewsletterCampaignsList(params, client)
  )
}


/**
 * Create Newsletter Campaign
 *
 * @method POST
 * @path /cfg/newsletter/campaigns/
 */
export function useCreateNewsletterCampaignsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: NewsletterCampaignRequest, client?: API): Promise<NewsletterCampaign> => {
    const result = await Fetchers.createNewsletterCampaignsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-campaigns')
    return result
  }
}


/**
 * Get Campaign Details
 *
 * @method GET
 * @path /cfg/newsletter/campaigns/{id}/
 */
export function useNewsletterCampaignsRetrieve(id: number, client?: API): ReturnType<typeof useSWR<NewsletterCampaign>> {
  return useSWR<NewsletterCampaign>(
    ['cfg-newsletter-campaign', id],
    () => Fetchers.getNewsletterCampaignsRetrieve(id, client)
  )
}


/**
 * Update Campaign
 *
 * @method PUT
 * @path /cfg/newsletter/campaigns/{id}/
 */
export function useUpdateNewsletterCampaignsUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: NewsletterCampaignRequest, client?: API): Promise<NewsletterCampaign> => {
    const result = await Fetchers.updateNewsletterCampaignsUpdate(id, data, client)
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
export function useDeleteNewsletterCampaignsDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: number, client?: API): Promise<void> => {
    const result = await Fetchers.deleteNewsletterCampaignsDestroy(id, client)
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
export function useCreateNewsletterCampaignsSendCreate() {
  const { mutate } = useSWRConfig()

  return async (data: SendCampaignRequest, client?: API): Promise<SendCampaignResponse> => {
    const result = await Fetchers.createNewsletterCampaignsSendCreate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-campaigns-send')
    return result
  }
}


