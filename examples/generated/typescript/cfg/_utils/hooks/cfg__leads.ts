/**
 * SWR Hooks for Leads
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
 * @path /django_cfg_leads/leads/
 */
export function useDjangoCfgLeadsLeads(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedLeadSubmissionList>(
    params ? ['django-cfg-leads-leads', params] : 'django-cfg-leads-leads',
    () => Fetchers.getDjangoCfgLeadsLeads(params)
  )
}

/**
 *
 * @method GET
 * @path /django_cfg_leads/leads/{id}/
 */
export function useDjangoCfgLeadsLead(id: number) {
  return useSWR<LeadSubmission>(
    ['django-cfg-leads-lead', id],
    () => Fetchers.getDjangoCfgLeadsLead(id)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /django_cfg_leads/leads/
 */
export function useCreateDjangoCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (data: LeadSubmissionRequest): Promise<LeadSubmission> => {
    const result = await Fetchers.createDjangoCfgLeadsLeads(data)

    // Revalidate related queries
    mutate('django-cfg-leads-leads')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /django_cfg_leads/leads/{id}/
 */
export function useUpdateDjangoCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: LeadSubmissionRequest): Promise<LeadSubmission> => {
    const result = await Fetchers.updateDjangoCfgLeadsLeads(id, data)

    // Revalidate related queries
    mutate('django-cfg-leads-leads')
    mutate('django-cfg-leads-lead')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /django_cfg_leads/leads/{id}/
 */
export function usePartialUpdateDjangoCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<LeadSubmission> => {
    const result = await Fetchers.partialUpdateDjangoCfgLeadsLeads(id)

    // Revalidate related queries
    mutate('django-cfg-leads-leads-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /django_cfg_leads/leads/{id}/
 */
export function useDeleteDjangoCfgLeadsLeads() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<void> => {
    const result = await Fetchers.deleteDjangoCfgLeadsLeads(id)

    // Revalidate related queries
    mutate('django-cfg-leads-leads')
    mutate('django-cfg-leads-lead')

    return result
  }
}
