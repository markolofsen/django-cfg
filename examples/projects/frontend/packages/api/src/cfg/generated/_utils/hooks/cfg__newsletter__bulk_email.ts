/**
 * SWR Hooks for Bulk Email
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
import * as Fetchers from '../fetchers/cfg__newsletter__bulk_email'
import type { API } from '../../index'
import type { BulkEmailRequest } from '../schemas/BulkEmailRequest.schema'
import type { BulkEmailResponse } from '../schemas/BulkEmailResponse.schema'

/**
 * Send Bulk Email
 *
 * @method POST
 * @path /cfg/newsletter/bulk/
 */
export function useCreateNewsletterBulkCreate() {
  const { mutate } = useSWRConfig()

  return async (data: BulkEmailRequest, client?: API): Promise<BulkEmailResponse> => {
    const result = await Fetchers.createNewsletterBulkCreate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-bulk')
    return result
  }
}


