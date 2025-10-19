/**
 * SWR Hooks for Leads
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
import * as Fetchers from '../fetchers/cfg__leads'
import type { API } from '../../index'
import type { LeadSubmission } from '../schemas/LeadSubmission.schema'
import type { LeadSubmissionRequest } from '../schemas/LeadSubmissionRequest.schema'
import type { PaginatedLeadSubmissionList } from '../schemas/PaginatedLeadSubmissionList.schema'
import type { PatchedLeadSubmissionRequest } from '../schemas/PatchedLeadSubmissionRequest.schema'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/leads/
 */
export function useLeadsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedLeadSubmissionList>> {
  return useSWR<PaginatedLeadSubmissionList>(
    params ? ['cfg-leads', params] : 'cfg-leads',
    () => Fetchers.getLeadsList(params, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/leads/
 */
export function useCreateLeadsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: LeadSubmissionRequest, client?: API): Promise<LeadSubmission> => {
    const result = await Fetchers.createLeadsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-leads')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/leads/{id}/
 */
export function useLeadsRetrieve(id: number, client?: API): ReturnType<typeof useSWR<LeadSubmission>> {
  return useSWR<LeadSubmission>(
    ['cfg-lead', id],
    () => Fetchers.getLeadsRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/leads/{id}/
 */
export function useUpdateLeadsUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: LeadSubmissionRequest, client?: API): Promise<LeadSubmission> => {
    const result = await Fetchers.updateLeadsUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-leads')
    mutate('cfg-lead')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/leads/{id}/
 */
export function usePartialUpdateLeadsPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data?: PatchedLeadSubmissionRequest, client?: API): Promise<LeadSubmission> => {
    const result = await Fetchers.partialUpdateLeadsPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-leads-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/leads/{id}/
 */
export function useDeleteLeadsDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: number, client?: API): Promise<void> => {
    const result = await Fetchers.deleteLeadsDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-leads')
    mutate('cfg-lead')
    return result
  }
}


