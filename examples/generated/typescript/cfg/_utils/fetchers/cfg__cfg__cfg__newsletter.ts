/**
 * Typed fetchers for Cfg Newsletter
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
import { UnsubscribeSchema, type Unsubscribe } from '../schemas/Unsubscribe.schema'
import { UnsubscribeRequestSchema, type UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * partialUpdateCfgNewsletterCampaigns
 *
 * Retrieve, update, or delete a newsletter campaign.
 *
 * @method PATCH
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function partialUpdateCfgNewsletterCampaigns(
  id: number,
  client?: API
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()

  const response = await api.cfg__newsletter.cfgNewsletterCampaignsPartialUpdate(id)
  return NewsletterCampaignSchema.parse(response)
}

/**
 * updateCfgNewsletterUnsubscribe
 *
 * Handle newsletter unsubscriptions.
 *
 * @method PUT
 * @path /cfg/newsletter/unsubscribe/
 */
export async function updateCfgNewsletterUnsubscribe(
  data: UnsubscribeRequest,
  client?: API
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()

  const response = await api.cfg__newsletter.cfgNewsletterUnsubscribeUpdate(data)
  return UnsubscribeSchema.parse(response)
}

/**
 * partialUpdateCfgNewsletterUnsubscribe
 *
 * Handle newsletter unsubscriptions.
 *
 * @method PATCH
 * @path /cfg/newsletter/unsubscribe/
 */
export async function partialUpdateCfgNewsletterUnsubscribe(
  client?: API
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()

  const response = await api.cfg__newsletter.cfgNewsletterUnsubscribePartialUpdate()
  return UnsubscribeSchema.parse(response)
}

