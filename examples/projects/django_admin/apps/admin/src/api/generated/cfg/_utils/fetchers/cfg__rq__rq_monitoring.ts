/**
 * Typed fetchers for RQ Monitoring
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
import { RQConfigSchema, type RQConfig } from '../schemas/RQConfig.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get RQ configuration
 *
 * @method GET
 * @path /cfg/rq/monitor/config/
 */
export async function getRqMonitorConfigRetrieve(  client?: any
): Promise<RQConfig> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_monitoring.rqMonitorConfigRetrieve()
  return RQConfigSchema.parse(response)
}


/**
 * Health check
 *
 * @method GET
 * @path /cfg/rq/monitor/health/
 */
export async function getRqMonitorHealthRetrieve(  client?: any
): Promise<HealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_monitoring.rqMonitorHealthRetrieve()
  return HealthCheckSchema.parse(response)
}


/**
 * Prometheus metrics
 *
 * @method GET
 * @path /cfg/rq/monitor/metrics/
 */
export async function getRqMonitorMetricsRetrieve(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_monitoring.rqMonitorMetricsRetrieve()
  return response
}


