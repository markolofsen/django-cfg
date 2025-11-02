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
import { HealthCheckSchema, type HealthCheck } from '../schemas/HealthCheck.schema'
import { MethodListSchema, type MethodList } from '../schemas/MethodList.schema'
import { OverviewStatsSchema, type OverviewStats } from '../schemas/OverviewStats.schema'
import { RecentRequestsSchema, type RecentRequests } from '../schemas/RecentRequests.schema'
import { ServiceListSchema, type ServiceList } from '../schemas/ServiceList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get gRPC health status
 *
 * @method GET
 * @path /cfg/grpc/monitor/health/
 */
export async function getGrpcMonitorHealthRetrieve(  client?: any
): Promise<HealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorHealthRetrieve()
  return HealthCheckSchema.parse(response)
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
): Promise<OverviewStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorOverviewRetrieve(params?.hours)
  return OverviewStatsSchema.parse(response)
}


/**
 * Get recent requests
 *
 * @method GET
 * @path /cfg/grpc/monitor/requests/
 */
export async function getGrpcMonitorRequestsRetrieve(  params?: { count?: number; method?: string; offset?: number; service?: string; status?: string },  client?: any
): Promise<RecentRequests> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorRequestsRetrieve(params?.count, params?.method, params?.offset, params?.service, params?.status)
  return RecentRequestsSchema.parse(response)
}


/**
 * Get service statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/services/
 */
export async function getGrpcMonitorServicesRetrieve(  params?: { hours?: number },  client?: any
): Promise<ServiceList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorServicesRetrieve(params?.hours)
  return ServiceListSchema.parse(response)
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


