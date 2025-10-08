/**
 * SWR Hooks for Bulk Email
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
import type { BulkEmailRequest } from '../schemas/BulkEmailRequest.schema'
import type { BulkEmailResponse } from '../schemas/BulkEmailResponse.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Send Bulk Email
 *
 * @method POST
 * @path /django_cfg_newsletter/bulk/
 */
export function useCreateDjangoCfgNewsletterBulk() {
  const { mutate } = useSWRConfig()

  return async (data: BulkEmailRequest): Promise<BulkEmailResponse> => {
    const result = await Fetchers.createDjangoCfgNewsletterBulk(data)

    // Revalidate related queries
    mutate('django-cfg-newsletter-bulk')

    return result
  }
}
