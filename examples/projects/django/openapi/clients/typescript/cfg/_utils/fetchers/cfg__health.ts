/**
 * Typed fetchers for Health
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
import { HealthCheckSchema, type HealthCheck } from '../schemas/HealthCheck.schema'
import { QuickHealthSchema, type QuickHealth } from '../schemas/QuickHealth.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/health/drf/
 */
export async function getHealthDrfRetrieve(  client?: API
): Promise<HealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_health.drfRetrieve()
  return HealthCheckSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/health/drf/quick/
 */
export async function getHealthDrfQuickRetrieve(  client?: API
): Promise<QuickHealth> {
  const api = client || getAPIInstance()
  const response = await api.cfg_health.drfQuickRetrieve()
  return QuickHealthSchema.parse(response)
}


