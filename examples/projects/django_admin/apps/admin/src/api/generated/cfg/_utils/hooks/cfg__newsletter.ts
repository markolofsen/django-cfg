/**
 * SWR Hooks for Newsletter
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
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__newsletter'
import type { API } from '../../index'
import type { NewsletterCampaign } from '../schemas/NewsletterCampaign.schema'
import type { PatchedNewsletterCampaignRequest } from '../schemas/PatchedNewsletterCampaignRequest.schema'
import type { PatchedUnsubscribeRequest } from '../schemas/PatchedUnsubscribeRequest.schema'
import type { Unsubscribe } from '../schemas/Unsubscribe.schema'
import type { UnsubscribeRequest } from '../schemas/UnsubscribeRequest.schema'

/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/newsletter/campaigns/{id}/
 */
export function usePartialUpdateNewsletterCampaignsPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data?: PatchedNewsletterCampaignRequest, client?: API): Promise<NewsletterCampaign> => {
    const result = await Fetchers.partialUpdateNewsletterCampaignsPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-campaigns-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/newsletter/unsubscribe/
 */
export function useUpdateNewsletterUnsubscribeUpdate() {
  const { mutate } = useSWRConfig()

  return async (data: UnsubscribeRequest, client?: API): Promise<Unsubscribe> => {
    const result = await Fetchers.updateNewsletterUnsubscribeUpdate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-unsubscribe')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/newsletter/unsubscribe/
 */
export function usePartialUpdateNewsletterUnsubscribePartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (data?: PatchedUnsubscribeRequest, client?: API): Promise<Unsubscribe> => {
    const result = await Fetchers.partialUpdateNewsletterUnsubscribePartialUpdate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-unsubscribe-partial')
    return result
  }
}


