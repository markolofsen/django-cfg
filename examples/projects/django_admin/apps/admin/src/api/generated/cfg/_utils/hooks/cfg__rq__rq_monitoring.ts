/**
 * SWR Hooks for RQ Monitoring
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
import * as Fetchers from '../fetchers/cfg__rq__rq_monitoring'
import type { API } from '../../index'
import type { HealthCheck } from '../schemas/HealthCheck.schema'
import type { RQConfig } from '../schemas/RQConfig.schema'

/**
 * Get RQ configuration
 *
 * @method GET
 * @path /cfg/rq/monitor/config/
 */
export function useRqMonitorConfigRetrieve(client?: API): ReturnType<typeof useSWR<RQConfig>> {
  return useSWR<RQConfig>(
    'cfg-rq-monitor-config',
    () => Fetchers.getRqMonitorConfigRetrieve(client)
  )
}


/**
 * Health check
 *
 * @method GET
 * @path /cfg/rq/monitor/health/
 */
export function useRqMonitorHealthRetrieve(client?: API): ReturnType<typeof useSWR<HealthCheck>> {
  return useSWR<HealthCheck>(
    'cfg-rq-monitor-health',
    () => Fetchers.getRqMonitorHealthRetrieve(client)
  )
}


/**
 * Prometheus metrics
 *
 * @method GET
 * @path /cfg/rq/monitor/metrics/
 */
export function useRqMonitorMetricsRetrieve(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-rq-monitor-metric',
    () => Fetchers.getRqMonitorMetricsRetrieve(client)
  )
}


