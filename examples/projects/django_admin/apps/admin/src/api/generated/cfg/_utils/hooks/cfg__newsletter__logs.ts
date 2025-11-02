/**
 * SWR Hooks for Logs
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
import * as Fetchers from '../fetchers/cfg__newsletter__logs'
import type { API } from '../../index'
import type { PaginatedEmailLogList } from '../schemas/PaginatedEmailLogList.schema'

/**
 * List Email Logs
 *
 * @method GET
 * @path /cfg/newsletter/logs/
 */
export function useNewsletterLogsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedEmailLogList>> {
  return useSWR<PaginatedEmailLogList>(
    params ? ['cfg-newsletter-logs', params] : 'cfg-newsletter-logs',
    () => Fetchers.getNewsletterLogsList(params, client)
  )
}


