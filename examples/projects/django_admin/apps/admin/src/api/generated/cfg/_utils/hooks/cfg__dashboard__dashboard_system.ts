/**
 * SWR Hooks for Dashboard - System
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_system'
import type { API } from '../../index'
import type { SystemHealth } from '../schemas/SystemHealth.schema'
import type { SystemMetrics } from '../schemas/SystemMetrics.schema'

/**
 * Get system health status
 *
 * @method GET
 * @path /cfg/dashboard/api/system/health/
 */
export function useDashboardApiSystemHealthRetrieve(client?: API): ReturnType<typeof useSWR<SystemHealth>> {
  return useSWR<SystemHealth>(
    'cfg-dashboard-api-system-health',
    () => Fetchers.getDashboardApiSystemHealthRetrieve(client)
  )
}


/**
 * Get system metrics
 *
 * @method GET
 * @path /cfg/dashboard/api/system/metrics/
 */
export function useDashboardApiSystemMetricsRetrieve(client?: API): ReturnType<typeof useSWR<SystemMetrics>> {
  return useSWR<SystemMetrics>(
    'cfg-dashboard-api-system-metric',
    () => Fetchers.getDashboardApiSystemMetricsRetrieve(client)
  )
}


