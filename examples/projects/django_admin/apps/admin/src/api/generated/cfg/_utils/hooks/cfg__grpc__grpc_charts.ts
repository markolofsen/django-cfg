/**
 * SWR Hooks for Grpc Charts
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
import * as Fetchers from '../fetchers/cfg__grpc__grpc_charts'
import type { API } from '../../index'
import type { DashboardCharts } from '../schemas/DashboardCharts.schema'
import type { ErrorDistributionChart } from '../schemas/ErrorDistributionChart.schema'
import type { RequestVolumeChart } from '../schemas/RequestVolumeChart.schema'
import type { ResponseTimeChart } from '../schemas/ResponseTimeChart.schema'
import type { ServerLifecycleChart } from '../schemas/ServerLifecycleChart.schema'
import type { ServerUptimeChart } from '../schemas/ServerUptimeChart.schema'
import type { ServiceActivityChart } from '../schemas/ServiceActivityChart.schema'

/**
 * Get all dashboard charts data
 *
 * @method GET
 * @path /cfg/grpc/charts/dashboard/
 */
export function useGrpcChartsDashboardRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<DashboardCharts>> {
  return useSWR<DashboardCharts>(
    params ? ['cfg-grpc-charts-dashboard', params] : 'cfg-grpc-charts-dashboard',
    () => Fetchers.getGrpcChartsDashboardRetrieve(params, client)
  )
}


/**
 * Get error distribution chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/error-distribution/
 */
export function useGrpcChartsErrorDistributionRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<ErrorDistributionChart>> {
  return useSWR<ErrorDistributionChart>(
    params ? ['cfg-grpc-charts-error-distribution', params] : 'cfg-grpc-charts-error-distribution',
    () => Fetchers.getGrpcChartsErrorDistributionRetrieve(params, client)
  )
}


/**
 * Get request volume chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/request-volume/
 */
export function useGrpcChartsRequestVolumeRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<RequestVolumeChart>> {
  return useSWR<RequestVolumeChart>(
    params ? ['cfg-grpc-charts-request-volume', params] : 'cfg-grpc-charts-request-volume',
    () => Fetchers.getGrpcChartsRequestVolumeRetrieve(params, client)
  )
}


/**
 * Get response time chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/response-time/
 */
export function useGrpcChartsResponseTimeRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<ResponseTimeChart>> {
  return useSWR<ResponseTimeChart>(
    params ? ['cfg-grpc-charts-response-time', params] : 'cfg-grpc-charts-response-time',
    () => Fetchers.getGrpcChartsResponseTimeRetrieve(params, client)
  )
}


/**
 * Get server lifecycle events
 *
 * @method GET
 * @path /cfg/grpc/charts/server-lifecycle/
 */
export function useGrpcChartsServerLifecycleRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<ServerLifecycleChart>> {
  return useSWR<ServerLifecycleChart>(
    params ? ['cfg-grpc-charts-server-lifecycle', params] : 'cfg-grpc-charts-server-lifecycle',
    () => Fetchers.getGrpcChartsServerLifecycleRetrieve(params, client)
  )
}


/**
 * Get server uptime chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/server-uptime/
 */
export function useGrpcChartsServerUptimeRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<ServerUptimeChart>> {
  return useSWR<ServerUptimeChart>(
    params ? ['cfg-grpc-charts-server-uptime', params] : 'cfg-grpc-charts-server-uptime',
    () => Fetchers.getGrpcChartsServerUptimeRetrieve(params, client)
  )
}


/**
 * Get service activity chart data
 *
 * @method GET
 * @path /cfg/grpc/charts/service-activity/
 */
export function useGrpcChartsServiceActivityRetrieve(params?: { hours?: number }, client?: API): ReturnType<typeof useSWR<ServiceActivityChart>> {
  return useSWR<ServiceActivityChart>(
    params ? ['cfg-grpc-charts-service-activity', params] : 'cfg-grpc-charts-service-activity',
    () => Fetchers.getGrpcChartsServiceActivityRetrieve(params, client)
  )
}


