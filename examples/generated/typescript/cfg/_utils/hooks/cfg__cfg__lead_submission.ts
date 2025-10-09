/**
 * SWR Hooks for Lead Submission
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
import type { LeadSubmissionRequest } from '../schemas/LeadSubmissionRequest.schema'
import type { LeadSubmissionResponse } from '../schemas/LeadSubmissionResponse.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Submit Lead Form
 *
 * @method POST
 * @path /cfg/leads/leads/submit/
 */
export function useCreateCfgLeadsLeadsSubmit() {
  const { mutate } = useSWRConfig()

  return async (data: LeadSubmissionRequest): Promise<LeadSubmissionResponse> => {
    const result = await Fetchers.createCfgLeadsLeadsSubmit(data)

    // Revalidate related queries
    mutate('cfg-leads-leads-submit')

    return result
  }
}
