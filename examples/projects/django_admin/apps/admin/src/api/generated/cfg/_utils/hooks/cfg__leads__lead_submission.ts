/**
 * SWR Hooks for Lead Submission
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
import * as Fetchers from '../fetchers/cfg__leads__lead_submission'
import type { API } from '../../index'
import type { LeadSubmissionRequest } from '../schemas/LeadSubmissionRequest.schema'
import type { LeadSubmissionResponse } from '../schemas/LeadSubmissionResponse.schema'

/**
 * Submit Lead Form
 *
 * @method POST
 * @path /cfg/leads/submit/
 */
export function useCreateLeadsSubmitCreate() {
  const { mutate } = useSWRConfig()

  return async (data: LeadSubmissionRequest, client?: API): Promise<LeadSubmissionResponse> => {
    const result = await Fetchers.createLeadsSubmitCreate(data, client)
    // Revalidate related queries
    mutate('cfg-leads-submit')
    return result
  }
}


