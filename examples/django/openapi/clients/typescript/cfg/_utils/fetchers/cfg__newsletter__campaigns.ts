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
import type { API } from '../../index'

/**
 * List Newsletter Campaigns
 *
 * Get a list of all newsletter campaigns.
 *
 * @method GET
 * @path /django_cfg_newsletter/campaigns/
 */
export async function getDjangoCfgNewsletterCampaignsList(
  params?: { page?: number; page_size?: number },
  client?: API
): Promise<PaginatedNewsletterCampaignList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_campaigns.list(params?.page, params?.page_size)
  return PaginatedNewsletterCampaignListSchema.parse(response)
}

/**
 * Create Newsletter Campaign
 *
 * Create a new newsletter campaign.
 *
 * @method POST
 * @path /django_cfg_newsletter/campaigns/
 */
export async function createDjangoCfgNewsletterCampaigns(
  data: NewsletterCampaignRequest,
  client?: API
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()

  const response = await api.cfg_campaigns.create(data)
  return NewsletterCampaignSchema.parse(response)
}

/**
 * Get Campaign Details
 *
 * Retrieve details of a specific newsletter campaign.
 *
 * @method GET
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export async function getDjangoCfgNewsletterCampaignsById(
  id: number,
  client?: API
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()

  const response = await api.cfg_campaigns.retrieve(id)
  return NewsletterCampaignSchema.parse(response)
}

/**
 * Update Campaign
 *
 * Update a newsletter campaign.
 *
 * @method PUT
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export async function updateDjangoCfgNewsletterCampaigns(
  id: number, data: NewsletterCampaignRequest,
  client?: API
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()

  const response = await api.cfg_campaigns.update(id, data)
  return NewsletterCampaignSchema.parse(response)
}

/**
 * Delete Campaign
 *
 * Delete a newsletter campaign.
 *
 * @method DELETE
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export async function deleteDjangoCfgNewsletterCampaigns(
  id: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_campaigns.destroy(id)
  return response
}

/**
 * Send Newsletter Campaign
 *
 * Send a newsletter campaign to all subscribers.
 *
 * @method POST
 * @path /django_cfg_newsletter/campaigns/send/
 */
export async function createDjangoCfgNewsletterCampaignsSend(
  data: SendCampaignRequest,
  client?: API
): Promise<SendCampaignResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_campaigns.sendCreate(data)
  return SendCampaignResponseSchema.parse(response)
}

