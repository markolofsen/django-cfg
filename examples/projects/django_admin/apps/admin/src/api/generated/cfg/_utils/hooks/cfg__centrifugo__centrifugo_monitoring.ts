/**
 * SWR Hooks for Centrifugo Monitoring
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
import * as Fetchers from '../fetchers/cfg__centrifugo__centrifugo_monitoring'
import type { API } from '../../index'
import type { CentrifugoOverviewStats } from '../schemas/CentrifugoOverviewStats.schema'
import type { ChannelList } from '../schemas/ChannelList.schema'
import type { HealthCheck } from '../schemas/HealthCheck.schema'
import type { PaginatedPublishList } from '../schemas/PaginatedPublishList.schema'

/**
 * Get Centrifugo health status
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/health/
 */
export function useCentrifugoMonitorHealthRetrieve(client?: API): ReturnType<typeof useSWR<HealthCheck>> {
  return useSWR<HealthCheck>(
    'cfg-centrifugo-monitor-health',
    () => Fetchers.getCentrifugoMonitorHealthRetrieve(client)
  )
}


/**
 * Get overview statistics
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/overview/
 */
export function useCentrifugoMonitorOverviewRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<CentrifugoOverviewStats>> {
  return useSWR<CentrifugoOverviewStats>(
    params ? ['cfg-centrifugo-monitor-overview', params] : 'cfg-centrifugo-monitor-overview',
    () => Fetchers.getCentrifugoMonitorOverviewRetrieve(params, client)
  )
}


/**
 * Get recent publishes
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/publishes/
 */
export function useCentrifugoMonitorPublishesList(params?: { channel?: string; page?: number; page_size?: number; status?: string }, client?: API): ReturnType<typeof useSWR<PaginatedPublishList>> {
  return useSWR<PaginatedPublishList>(
    params ? ['cfg-centrifugo-monitor-publishes', params] : 'cfg-centrifugo-monitor-publishes',
    () => Fetchers.getCentrifugoMonitorPublishesList(params, client)
  )
}


/**
 * Get channel statistics
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/timeline/
 */
export function useCentrifugoMonitorTimelineRetrieve(params?: { hours?: number; interval?: string }, client?: API): ReturnType<typeof useSWR<ChannelList>> {
  return useSWR<ChannelList>(
    params ? ['cfg-centrifugo-monitor-timeline', params] : 'cfg-centrifugo-monitor-timeline',
    () => Fetchers.getCentrifugoMonitorTimelineRetrieve(params, client)
  )
}


