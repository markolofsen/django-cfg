/**
 * SWR Hooks for Newsletters
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
import type { Newsletter } from '../schemas/Newsletter.schema'
import type { PaginatedNewsletterList } from '../schemas/PaginatedNewsletterList.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List Active Newsletters
 *
 * @method GET
 * @path /cfg/newsletter/newsletters/
 */
export function useCfgNewsletterNewslettersList(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedNewsletterList>(
    params ? ['cfg-newsletter-newsletters', params] : 'cfg-newsletter-newsletters',
    () => Fetchers.getCfgNewsletterNewslettersList(params)
  )
}

/**
 * Get Newsletter Details
 *
 * @method GET
 * @path /cfg/newsletter/newsletters/{id}/
 */
export function useCfgNewsletterNewslettersById(id: number) {
  return useSWR<Newsletter>(
    ['cfg-newsletter-newsletter', id],
    () => Fetchers.getCfgNewsletterNewslettersById(id)
  )
}
