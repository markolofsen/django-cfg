/**
 * SWR Hooks for Cfg Leads
 *
 * Auto-generated React hooks for data fetching with SWR.
 *
 * Setup:
 * ```typescript
 * // Configure API once (in your app root)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 * ```
 *
 * Usage:
 * ```typescript
 * // Query hook
 * const { data, error, mutate } = useShopProducts({ page: 1 })
 *
 * // Mutation hook
 * const createProduct = useCreateShopProduct()
 * await createProduct({ name: 'Product', price: 99 })
 * ```
 */
import type { LeadSubmission } from '../schemas/LeadSubmission.schema'
import type { LeadSubmissionRequest } from '../schemas/LeadSubmissionRequest.schema'
import type { PaginatedLeadSubmissionList } from '../schemas/PaginatedLeadSubmissionList.schema'
import type { PatchedLeadSubmissionRequest } from '../schemas/PatchedLeadSubmissionRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 *
 * @method GET
 * @path /cfg/leads/leads/
 */
export function useCfgLeadsLeadsList(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedLeadSubmissionList>(
    params ? ['cfg-leads-leads', params] : 'cfg-leads-leads',
    () => Fetchers.getCfgLeadsLeadsList(params)
  )
}

/**
 *
 * @method GET
 * @path /cfg/leads/leads/{id}/
 */
export function useCfgLeadsLeadsById(id: number) {
  return useSWR<LeadSubmission>(
    ['cfg-leads-lead', id],
    () => Fetchers.getCfgLeadsLeadsById(id)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /cfg/leads/leads/
 */
export function useCreateCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (data: LeadSubmissionRequest): Promise<LeadSubmission> => {
    const result = await Fetchers.createCfgLeadsLeads(data)

    // Revalidate related queries
    mutate('cfg-leads-leads')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/leads/leads/{id}/
 */
export function useUpdateCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: LeadSubmissionRequest): Promise<LeadSubmission> => {
    const result = await Fetchers.updateCfgLeadsLeads(id, data)

    // Revalidate related queries
    mutate('cfg-leads-leads')
    mutate('cfg-leads-lead')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/leads/leads/{id}/
 */
export function usePartialUpdateCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<LeadSubmission> => {
    const result = await Fetchers.partialUpdateCfgLeadsLeads(id)

    // Revalidate related queries
    mutate('cfg-leads-leads-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/leads/leads/{id}/
 */
export function useDeleteCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<void> => {
    const result = await Fetchers.deleteCfgLeadsLeads(id)

    // Revalidate related queries
    mutate('cfg-leads-leads')
    mutate('cfg-leads-lead')

    return result
  }
}
