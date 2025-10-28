/**
 * Typed fetchers for Campaigns
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
import { NewsletterCampaignSchema, type NewsletterCampaign } from '../schemas/NewsletterCampaign.schema'
import { NewsletterCampaignRequestSchema, type NewsletterCampaignRequest } from '../schemas/NewsletterCampaignRequest.schema'
import { PaginatedNewsletterCampaignListSchema, type PaginatedNewsletterCampaignList } from '../schemas/PaginatedNewsletterCampaignList.schema'
import { SendCampaignRequestSchema, type SendCampaignRequest } from '../schemas/SendCampaignRequest.schema'
import { SendCampaignResponseSchema, type SendCampaignResponse } from '../schemas/SendCampaignResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List Newsletter Campaigns
 *
 * @method GET
 * @path /cfg/newsletter/campaigns/
 */
export async function getNewsletterCampaignsList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedNewsletterCampaignList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsList(params?.page, params?.page_size)
  return PaginatedNewsletterCampaignListSchema.parse(response)
}


/**
 * Create Newsletter Campaign
 *
 * @method POST
 * @path /cfg/newsletter/campaigns/
 */
export async function createNewsletterCampaignsCreate(  data: NewsletterCampaignRequest,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsCreate(data)
  return NewsletterCampaignSchema.parse(response)
}


/**
 * Get Campaign Details
 *
 * @method GET
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function getNewsletterCampaignsRetrieve(  id: number,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsRetrieve(id)
  return NewsletterCampaignSchema.parse(response)
}


/**
 * Update Campaign
 *
 * @method PUT
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function updateNewsletterCampaignsUpdate(  id: number, data: NewsletterCampaignRequest,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsUpdate(id, data)
  return NewsletterCampaignSchema.parse(response)
}


/**
 * Delete Campaign
 *
 * @method DELETE
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function deleteNewsletterCampaignsDestroy(  id: number,  client?: any
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsDestroy(id)
  return response
}


/**
 * Send Newsletter Campaign
 *
 * @method POST
 * @path /cfg/newsletter/campaigns/send/
 */
export async function createNewsletterCampaignsSendCreate(  data: SendCampaignRequest,  client?: any
): Promise<SendCampaignResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_campaigns.newsletterCampaignsSendCreate(data)
  return SendCampaignResponseSchema.parse(response)
}


