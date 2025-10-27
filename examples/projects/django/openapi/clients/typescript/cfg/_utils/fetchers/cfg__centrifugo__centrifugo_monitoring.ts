/**
 * Typed fetchers for Centrifugo Monitoring
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
import { ChannelListSchema, type ChannelList } from '../schemas/ChannelList.schema'
import { HealthCheckSchema, type HealthCheck } from '../schemas/HealthCheck.schema'
import { OverviewStatsSchema, type OverviewStats } from '../schemas/OverviewStats.schema'
import { RecentPublishesSchema, type RecentPublishes } from '../schemas/RecentPublishes.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Get Centrifugo health status
 *
 * @method GET
 * @path /cfg/centrifugo/admin/api/monitor/health/
 */
export async function getCentrifugoAdminApiMonitorHealthRetrieve(  client?: API
): Promise<HealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoAdminApiMonitorHealthRetrieve()
  return HealthCheckSchema.parse(response)
}


/**
 * Get overview statistics
 *
 * @method GET
 * @path /cfg/centrifugo/admin/api/monitor/overview/
 */
export async function getCentrifugoAdminApiMonitorOverviewRetrieve(  params?: { hours?: number },  client?: API
): Promise<OverviewStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoAdminApiMonitorOverviewRetrieve(params?.hours)
  return OverviewStatsSchema.parse(response)
}


/**
 * Get recent publishes
 *
 * @method GET
 * @path /cfg/centrifugo/admin/api/monitor/publishes/
 */
export async function getCentrifugoAdminApiMonitorPublishesRetrieve(  params?: { channel?: string; count?: number; offset?: number; status?: string },  client?: API
): Promise<RecentPublishes> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoAdminApiMonitorPublishesRetrieve(params?.channel, params?.count, params?.offset, params?.status)
  return RecentPublishesSchema.parse(response)
}


/**
 * Get channel statistics
 *
 * @method GET
 * @path /cfg/centrifugo/admin/api/monitor/timeline/
 */
export async function getCentrifugoAdminApiMonitorTimelineRetrieve(  params?: { hours?: number; interval?: string },  client?: API
): Promise<ChannelList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoAdminApiMonitorTimelineRetrieve(params?.hours, params?.interval)
  return ChannelListSchema.parse(response)
}


/**
 * Get Centrifugo health status
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/health/
 */
export async function getCentrifugoMonitorHealthRetrieve(  client?: API
): Promise<HealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorHealthRetrieve()
  return HealthCheckSchema.parse(response)
}


/**
 * Get overview statistics
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/overview/
 */
export async function getCentrifugoMonitorOverviewRetrieve(  params?: { hours?: number },  client?: API
): Promise<OverviewStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorOverviewRetrieve(params?.hours)
  return OverviewStatsSchema.parse(response)
}


/**
 * Get recent publishes
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/publishes/
 */
export async function getCentrifugoMonitorPublishesRetrieve(  params?: { channel?: string; count?: number; offset?: number; status?: string },  client?: API
): Promise<RecentPublishes> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorPublishesRetrieve(params?.channel, params?.count, params?.offset, params?.status)
  return RecentPublishesSchema.parse(response)
}


/**
 * Get channel statistics
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/timeline/
 */
export async function getCentrifugoMonitorTimelineRetrieve(  params?: { hours?: number; interval?: string },  client?: API
): Promise<ChannelList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorTimelineRetrieve(params?.hours, params?.interval)
  return ChannelListSchema.parse(response)
}


