/**
 * SWR Hooks for Newsletters
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
import * as Fetchers from '../fetchers/cfg__newsletter__newsletters'
import type { API } from '../../index'
import type { Newsletter } from '../schemas/Newsletter.schema'
import type { PaginatedNewsletterList } from '../schemas/PaginatedNewsletterList.schema'

/**
 * List Active Newsletters
 *
 * @method GET
 * @path /cfg/newsletter/newsletters/
 */
export function useNewsletterNewslettersList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedNewsletterList>> {
  return useSWR<PaginatedNewsletterList>(
    params ? ['cfg-newsletter-newsletters', params] : 'cfg-newsletter-newsletters',
    () => Fetchers.getNewsletterNewslettersList(params, client)
  )
}


/**
 * Get Newsletter Details
 *
 * @method GET
 * @path /cfg/newsletter/newsletters/{id}/
 */
export function useNewsletterNewslettersRetrieve(id: number, client?: API): ReturnType<typeof useSWR<Newsletter>> {
  return useSWR<Newsletter>(
    ['cfg-newsletter-newsletter', id],
    () => Fetchers.getNewsletterNewslettersRetrieve(id, client)
  )
}


