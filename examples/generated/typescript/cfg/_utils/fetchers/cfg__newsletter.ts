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
import { UnsubscribeSchema, type Unsubscribe } from '../schemas/Unsubscribe.schema'
import { UnsubscribeRequestSchema, type UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * partialUpdateDjangoCfgNewsletterCampaigns
 *
 * Retrieve, update, or delete a newsletter campaign.
 *
 * @method PATCH
 * @path /django_cfg_newsletter/campaigns/{id}/
 */
export async function partialUpdateDjangoCfgNewsletterCampaigns(
  id: number,
  client?: API
): Promise<NewsletterCampaign> {
  const api = client || getAPIInstance()

  const response = await api.cfg_newsletter.campaignsPartialUpdate(id)
  return NewsletterCampaignSchema.parse(response)
}

/**
 * updateDjangoCfgNewsletterUnsubscribe
 *
 * Handle newsletter unsubscriptions.
 *
 * @method PUT
 * @path /django_cfg_newsletter/unsubscribe/
 */
export async function updateDjangoCfgNewsletterUnsubscribe(
  data: UnsubscribeRequest,
  client?: API
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()

  const response = await api.cfg_newsletter.unsubscribeUpdate(data)
  return UnsubscribeSchema.parse(response)
}

/**
 * partialUpdateDjangoCfgNewsletterUnsubscribe
 *
 * Handle newsletter unsubscriptions.
 *
 * @method PATCH
 * @path /django_cfg_newsletter/unsubscribe/
 */
export async function partialUpdateDjangoCfgNewsletterUnsubscribe(
  client?: API
): Promise<Unsubscribe> {
  const api = client || getAPIInstance()

  const response = await api.cfg_newsletter.unsubscribePartialUpdate()
  return UnsubscribeSchema.parse(response)
}

