/**
 * Typed fetchers for Subscriptions
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
import { PaginatedNewsletterSubscriptionListSchema, type PaginatedNewsletterSubscriptionList } from '../schemas/PaginatedNewsletterSubscriptionList.schema'
import { SubscribeRequestSchema, type SubscribeRequest } from '../schemas/SubscribeRequest.schema'
import { SubscribeResponseSchema, type SubscribeResponse } from '../schemas/SubscribeResponse.schema'
import { SuccessResponseSchema, type SuccessResponse } from '../schemas/SuccessResponse.schema'
import { UnsubscribeRequestSchema, type UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Subscribe to Newsletter
 *
 * Subscribe an email address to a newsletter.
 *
 * @method POST
 * @path /django_cfg_newsletter/subscribe/
 */
export async function createDjangoCfgNewsletterSubscribe(
  data: SubscribeRequest,
  client?: API
): Promise<SubscribeResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_subscriptions.subscribeCreate(data)
  return SubscribeResponseSchema.parse(response)
}

/**
 * List User Subscriptions
 *
 * Get a list of current user's active newsletter subscriptions.
 *
 * @method GET
 * @path /django_cfg_newsletter/subscriptions/
 */
export async function getDjangoCfgNewsletterSubscriptionsList(
  params?: { page?: number; page_size?: number },
  client?: API
): Promise<PaginatedNewsletterSubscriptionList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_subscriptions.list(params?.page, params?.page_size)
  return PaginatedNewsletterSubscriptionListSchema.parse(response)
}

/**
 * Unsubscribe from Newsletter
 *
 * Unsubscribe from a newsletter using subscription ID.
 *
 * @method POST
 * @path /django_cfg_newsletter/unsubscribe/
 */
export async function createDjangoCfgNewsletterUnsubscribe(
  data: UnsubscribeRequest,
  client?: API
): Promise<SuccessResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_subscriptions.unsubscribeCreate(data)
  return SuccessResponseSchema.parse(response)
}

