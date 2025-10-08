/**
 * Typed fetchers for Logs
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { PaginatedEmailLogListSchema, type PaginatedEmailLogList } from '../schemas/PaginatedEmailLogList.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List Email Logs
 *
 * Get a list of email sending logs.
 *
 * @method GET
 * @path /django_cfg_newsletter/logs/
 */
export async function getDjangoCfgNewsletterLogsList(
  params?: { page?: number; page_size?: number },
  client?: API
): Promise<PaginatedEmailLogList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_logs.list(params?.page, params?.page_size)
  return PaginatedEmailLogListSchema.parse(response)
}

