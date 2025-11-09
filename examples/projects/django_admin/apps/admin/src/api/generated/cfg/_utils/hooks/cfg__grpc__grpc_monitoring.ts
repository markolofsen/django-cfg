/**
 * SWR Hooks for Grpc Monitoring
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
import * as Fetchers from '../fetchers/cfg__grpc__grpc_monitoring'
import type { API } from '../../index'
import type { GRPCHealthCheck } from '../schemas/GRPCHealthCheck.schema'
import type { GRPCOverviewStats } from '../schemas/GRPCOverviewStats.schema'
import type { MethodList } from '../schemas/MethodList.schema'
import type { PaginatedRecentRequestList } from '../schemas/PaginatedRecentRequestList.schema'

/**
 * Get gRPC health status
 *
 * @method GET
 * @path /cfg/grpc/monitor/health/
 */
export function useGrpcMonitorHealthRetrieve(client?: API): ReturnType<typeof useSWR<GRPCHealthCheck>> {
  return useSWR<GRPCHealthCheck>(
    'cfg-grpc-monitor-health',
    () => Fetchers.getGrpcMonitorHealthRetrieve(client)
  )
}


/**
 * Get method statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/methods/
 */
export function useGrpcMonitorMethodsRetrieve(params?: { hours?: number; service?: string }, client?: API): ReturnType<typeof useSWR<MethodList>> {
  return useSWR<MethodList>(
    params ? ['cfg-grpc-monitor-method', params] : 'cfg-grpc-monitor-method',
    () => Fetchers.getGrpcMonitorMethodsRetrieve(params, client)
  )
}


/**
 * Get overview statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/overview/
 */
export function useGrpcMonitorOverviewRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<GRPCOverviewStats>> {
  return useSWR<GRPCOverviewStats>(
    params ? ['cfg-grpc-monitor-overview', params] : 'cfg-grpc-monitor-overview',
    () => Fetchers.getGrpcMonitorOverviewRetrieve(params, client)
  )
}


/**
 * Get recent requests
 *
 * @method GET
 * @path /cfg/grpc/monitor/requests/
 */
export function useGrpcMonitorRequestsList(params?: { method?: string; page?: number; page_size?: number; service?: string; status?: string }, client?: API): ReturnType<typeof useSWR<PaginatedRecentRequestList>> {
  return useSWR<PaginatedRecentRequestList>(
    params ? ['cfg-grpc-monitor-requests', params] : 'cfg-grpc-monitor-requests',
    () => Fetchers.getGrpcMonitorRequestsList(params, client)
  )
}


/**
 * Get request timeline
 *
 * @method GET
 * @path /cfg/grpc/monitor/timeline/
 */
export function useGrpcMonitorTimelineRetrieve(params?: { hours?: number; interval?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-grpc-monitor-timeline', params] : 'cfg-grpc-monitor-timeline',
    () => Fetchers.getGrpcMonitorTimelineRetrieve(params, client)
  )
}


