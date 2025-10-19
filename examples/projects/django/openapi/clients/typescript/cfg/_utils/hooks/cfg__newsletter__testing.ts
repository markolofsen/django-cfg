/**
 * SWR Hooks for Testing
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
import * as Fetchers from '../fetchers/cfg__newsletter__testing'
import type { API } from '../../index'
import type { BulkEmailResponse } from '../schemas/BulkEmailResponse.schema'
import type { TestEmailRequest } from '../schemas/TestEmailRequest.schema'

/**
 * Test Email Sending
 *
 * @method POST
 * @path /cfg/newsletter/test/
 */
export function useCreateNewsletterTestCreate() {
  const { mutate } = useSWRConfig()

  return async (data: TestEmailRequest, client?: API): Promise<BulkEmailResponse> => {
    const result = await Fetchers.createNewsletterTestCreate(data, client)
    // Revalidate related queries
    mutate('cfg-newsletter-test')
    return result
  }
}


