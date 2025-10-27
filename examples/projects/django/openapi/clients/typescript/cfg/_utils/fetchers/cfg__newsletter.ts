/**
 * Typed fetchers for Newsletter
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
import { PatchedNewsletterCampaignRequestSchema, type PatchedNewsletterCampaignRequest } from '../schemas/PatchedNewsletterCampaignRequest.schema'
import { PatchedUnsubscribeRequestSchema, type PatchedUnsubscribeRequest } from '../schemas/PatchedUnsubscribeRequest.schema'
import { UnsubscribeSchema, type Unsubscribe } from '../schemas/Unsubscribe.schema'
import { UnsubscribeRequestSchema, type UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/newsletter/campaigns/{id}/
 */
export async function partialUpdateNewsletterCampaignsPartialUpdate(  id: number, data?: PatchedNewsletterCampaignRequest,  client?: any
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()
  const response = await api.cfg_newsletter.campaignsPartialUpdate(id, data)
  return NewsletterCampaignSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/newsletter/unsubscribe/
 */
export async function updateNewsletterUnsubscribeUpdate(  data: UnsubscribeRequest,  client?: any
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()
  const response = await api.cfg_newsletter.unsubscribeUpdate(data)
  return UnsubscribeSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/newsletter/unsubscribe/
 */
export async function partialUpdateNewsletterUnsubscribePartialUpdate(  data?: PatchedUnsubscribeRequest,  client?: any
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()
  const response = await api.cfg_newsletter.unsubscribePartialUpdate(data)
  return UnsubscribeSchema.parse(response)
}


