/**
 * Typed fetchers for Dashboard - System
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
import { SystemHealthSchema, type SystemHealth } from '../schemas/SystemHealth.schema'
import { SystemMetricsSchema, type SystemMetrics } from '../schemas/SystemMetrics.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Get system health status
 *
 * @method GET
 * @path /cfg/dashboard/api/system/health/
 */
export async function getDashboardApiSystemHealthRetrieve(  client?: API
): Promise<SystemHealth> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_system.dashboardApiSystemHealthRetrieve()
  return SystemHealthSchema.parse(response)
}


/**
 * Get system metrics
 *
 * @method GET
 * @path /cfg/dashboard/api/system/metrics/
 */
export async function getDashboardApiSystemMetricsRetrieve(  client?: API
): Promise<SystemMetrics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_system.dashboardApiSystemMetricsRetrieve()
  return SystemMetricsSchema.parse(response)
}


