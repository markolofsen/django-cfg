/**
 * SWR Hooks for Testing
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
import type { BulkEmailResponse } from '../schemas/BulkEmailResponse.schema'
import type { TestEmailRequest } from '../schemas/TestEmailRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Test Email Sending
 *
 * @method POST
 * @path /django_cfg_newsletter/test/
 */
export function useCreateDjangoCfgNewsletterTest() {
  const { mutate } = useSWRConfig()

  return async (data: TestEmailRequest): Promise<BulkEmailResponse> => {
    const result = await Fetchers.createDjangoCfgNewsletterTest(data)

    // Revalidate related queries
    mutate('django-cfg-newsletter-test')

    return result
  }
}
