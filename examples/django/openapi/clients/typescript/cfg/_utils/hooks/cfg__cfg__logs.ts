/**
 * SWR Hooks for Logs
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
import type { PaginatedEmailLogList } from '../schemas/PaginatedEmailLogList.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List Email Logs
 *
 * @method GET
 * @path /cfg/newsletter/logs/
 */
export function useCfgNewsletterLogsList(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedEmailLogList>(
    params ? ['cfg-newsletter-logs', params] : 'cfg-newsletter-logs',
    () => Fetchers.getCfgNewsletterLogsList(params)
  )
}
