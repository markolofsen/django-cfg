/**
 * SWR Hooks for Subscriptions
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
import * as Fetchers from '../fetchers/cfg__newsletter__subscriptions'
import type { API } from '../../index'
import type { PaginatedNewsletterSubscriptionList } from '../schemas/PaginatedNewsletterSubscriptionList.schema'
import type { SubscribeRequest } from '../schemas/SubscribeRequest.schema'
import type { SubscribeResponse } from '../schemas/SubscribeResponse.schema'
import type { SuccessResponse } from '../schemas/SuccessResponse.schema'
import type { UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'

/**
 * Subscribe to Newsletter
 *
 * @method POST
 * @path /cfg/newsletter/subscribe/
 */
export function useCreateNewsletterSubscribeCreate() {
  const { mutate } = useSWRConfig()

  return async (data: SubscribeRequest, client?: API): Promise<SubscribeResponse> => {
    const result = await Fetchers.createNewsletterSubscribeCreate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-subscribe')
    return result
  }
}


/**
 * List User Subscriptions
 *
 * @method GET
 * @path /cfg/newsletter/subscriptions/
 */
export function useNewsletterSubscriptionsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedNewsletterSubscriptionList>> {
  return useSWR<PaginatedNewsletterSubscriptionList>(
    params ? ['cfg-newsletter-subscriptions', params] : 'cfg-newsletter-subscriptions',
    () => Fetchers.getNewsletterSubscriptionsList(params, client)
  )
}


/**
 * Unsubscribe from Newsletter
 *
 * @method POST
 * @path /cfg/newsletter/unsubscribe/
 */
export function useCreateNewsletterUnsubscribeCreate() {
  const { mutate } = useSWRConfig()

  return async (data: UnsubscribeRequest, client?: API): Promise<SuccessResponse> => {
    const result = await Fetchers.createNewsletterUnsubscribeCreate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-unsubscribe')
    return result
  }
}


