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
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__grpc__grpc_monitoring'
import type { API } from '../../index'
import type { HealthCheck } from '../schemas/HealthCheck.schema'
import type { MethodList } from '../schemas/MethodList.schema'
import type { OverviewStats } from '../schemas/OverviewStats.schema'
import type { RecentRequests } from '../schemas/RecentRequests.schema'
import type { ServiceList } from '../schemas/ServiceList.schema'

/**
 * Get gRPC health status
 *
 * @method GET
 * @path /cfg/grpc/monitor/health/
 */
export function useGrpcMonitorHealthRetrieve(client?: API): ReturnType<typeof useSWR<HealthCheck>> {
  return useSWR<HealthCheck>(
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
export function useGrpcMonitorOverviewRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<OverviewStats>> {
  return useSWR<OverviewStats>(
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
export function useGrpcMonitorRequestsRetrieve(params?: { count?: number; method?: string; offset?: number; service?: string; status?: string }, client?: API): ReturnType<typeof useSWR<RecentRequests>> {
  return useSWR<RecentRequests>(
    params ? ['cfg-grpc-monitor-request', params] : 'cfg-grpc-monitor-request',
    () => Fetchers.getGrpcMonitorRequestsRetrieve(params, client)
  )
}


/**
 * Get service statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/services/
 */
export function useGrpcMonitorServicesRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<ServiceList>> {
  return useSWR<ServiceList>(
    params ? ['cfg-grpc-monitor-service', params] : 'cfg-grpc-monitor-service',
    () => Fetchers.getGrpcMonitorServicesRetrieve(params, client)
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


