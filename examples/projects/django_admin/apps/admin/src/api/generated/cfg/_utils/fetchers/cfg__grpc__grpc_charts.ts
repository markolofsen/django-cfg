/**
 * Typed fetchers for Grpc Charts
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
import { DashboardChartsSchema, type DashboardCharts } from '../schemas/DashboardCharts.schema'
import { ErrorDistributionChartSchema, type ErrorDistributionChart } from '../schemas/ErrorDistributionChart.schema'
import { RequestVolumeChartSchema, type RequestVolumeChart } from '../schemas/RequestVolumeChart.schema'
import { ResponseTimeChartSchema, type ResponseTimeChart } from '../schemas/ResponseTimeChart.schema'
import { ServerLifecycleChartSchema, type ServerLifecycleChart } from '../schemas/ServerLifecycleChart.schema'
import { ServerUptimeChartSchema, type ServerUptimeChart } from '../schemas/ServerUptimeChart.schema'
import { ServiceActivityChartSchema, type ServiceActivityChart } from '../schemas/ServiceActivityChart.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get all dashboard charts data
 *
 * @method GET
 * @path /cfg/grpc/charts/dashboard/
 */
export async function getGrpcChartsDashboardRetrieve(  params?: { hours?: number },  client?: any
): Promise<DashboardCharts> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_charts.dashboardRetrieve(params?.hours)
  return DashboardChartsSchema.parse(response)
}


/**
 * Get error distribution chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/error-distribution/
 */
export async function getGrpcChartsErrorDistributionRetrieve(  params?: { hours?: number },  client?: any
): Promise<ErrorDistributionChart> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_charts.errorDistributionRetrieve(params?.hours)
  return ErrorDistributionChartSchema.parse(response)
}


/**
 * Get request volume chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/request-volume/
 */
export async function getGrpcChartsRequestVolumeRetrieve(  params?: { hours?: number },  client?: any
): Promise<RequestVolumeChart> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_charts.requestVolumeRetrieve(params?.hours)
  return RequestVolumeChartSchema.parse(response)
}


/**
 * Get response time chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/response-time/
 */
export async function getGrpcChartsResponseTimeRetrieve(  params?: { hours?: number },  client?: any
): Promise<ResponseTimeChart> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_charts.responseTimeRetrieve(params?.hours)
  return ResponseTimeChartSchema.parse(response)
}


/**
 * Get server lifecycle events
 *
 * @method GET
 * @path /cfg/grpc/charts/server-lifecycle/
 */
export async function getGrpcChartsServerLifecycleRetrieve(  params?: { hours?: number },  client?: any
): Promise<ServerLifecycleChart> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_charts.serverLifecycleRetrieve(params?.hours)
  return ServerLifecycleChartSchema.parse(response)
}


/**
 * Get server uptime chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/server-uptime/
 */
export async function getGrpcChartsServerUptimeRetrieve(  params?: { hours?: number },  client?: any
): Promise<ServerUptimeChart> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_charts.serverUptimeRetrieve(params?.hours)
  return ServerUptimeChartSchema.parse(response)
}


/**
 * Get service activity chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/service-activity/
 */
export async function getGrpcChartsServiceActivityRetrieve(  params?: { hours?: number },  client?: any
): Promise<ServiceActivityChart> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_charts.serviceActivityRetrieve(params?.hours)
  return ServiceActivityChartSchema.parse(response)
}


