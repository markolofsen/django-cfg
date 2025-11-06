/**
 * Typed fetchers for Grpc Monitoring
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
import { GRPCHealthCheckSchema, type GRPCHealthCheck } from '../schemas/GRPCHealthCheck.schema'
import { GRPCOverviewStatsSchema, type GRPCOverviewStats } from '../schemas/GRPCOverviewStats.schema'
import { MethodListSchema, type MethodList } from '../schemas/MethodList.schema'
import { PaginatedRecentRequestListSchema, type PaginatedRecentRequestList } from '../schemas/PaginatedRecentRequestList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get gRPC health status
 *
 * @method GET
 * @path /cfg/grpc/monitor/health/
 */
export async function getGrpcMonitorHealthRetrieve(  client?: any
): Promise<GRPCHealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorHealthRetrieve()
  return GRPCHealthCheckSchema.parse(response)
}


/**
 * Get method statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/methods/
 */
export async function getGrpcMonitorMethodsRetrieve(  params?: { hours?: number; service?: string },  client?: any
): Promise<MethodList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorMethodsRetrieve(params?.hours, params?.service)
  return MethodListSchema.parse(response)
}


/**
 * Get overview statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/overview/
 */
export async function getGrpcMonitorOverviewRetrieve(  params?: { hours?: number },  client?: any
): Promise<GRPCOverviewStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorOverviewRetrieve(params?.hours)
  return GRPCOverviewStatsSchema.parse(response)
}


/**
 * Get recent requests
 *
 * @method GET
 * @path /cfg/grpc/monitor/requests/
 */
export async function getGrpcMonitorRequestsList(  params?: { method?: string; page?: number; page_size?: number; service?: string; status?: string },  client?: any
): Promise<PaginatedRecentRequestList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorRequestsList(params?.method, params?.page, params?.page_size, params?.service, params?.status)
  return PaginatedRecentRequestListSchema.parse(response)
}


/**
 * Get request timeline
 *
 * @method GET
 * @path /cfg/grpc/monitor/timeline/
 */
export async function getGrpcMonitorTimelineRetrieve(  params?: { hours?: number; interval?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorTimelineRetrieve(params?.hours, params?.interval)
  return response
}


