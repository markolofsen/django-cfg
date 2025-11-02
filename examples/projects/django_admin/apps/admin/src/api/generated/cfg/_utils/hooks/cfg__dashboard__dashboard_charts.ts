/**
 * SWR Hooks for Dashboard - Charts
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_charts'
import type { API } from '../../index'
import type { ChartData } from '../schemas/ChartData.schema'

/**
 * Get user activity chart
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/activity/
 */
export function useDashboardApiChartsActivityRetrieve(params?: { days?: number }, client?: API): ReturnType<typeof useSWR<ChartData>> {
  return useSWR<ChartData>(
    params ? ['cfg-dashboard-api-charts-activity', params] : 'cfg-dashboard-api-charts-activity',
    () => Fetchers.getDashboardApiChartsActivityRetrieve(params, client)
  )
}


/**
 * Get recent users
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/recent-users/
 */
export function useDashboardApiChartsRecentUsersList(params?: { limit?: number }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-dashboard-api-charts-recent-users', params] : 'cfg-dashboard-api-charts-recent-users',
    () => Fetchers.getDashboardApiChartsRecentUsersList(params, client)
  )
}


/**
 * Get user registration chart
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/registrations/
 */
export function useDashboardApiChartsRegistrationsRetrieve(params?: { days?: number }, client?: API): ReturnType<typeof useSWR<ChartData>> {
  return useSWR<ChartData>(
    params ? ['cfg-dashboard-api-charts-registration', params] : 'cfg-dashboard-api-charts-registration',
    () => Fetchers.getDashboardApiChartsRegistrationsRetrieve(params, client)
  )
}


/**
 * Get activity tracker
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/tracker/
 */
export function useDashboardApiChartsTrackerList(params?: { weeks?: number }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-dashboard-api-charts-tracker', params] : 'cfg-dashboard-api-charts-tracker',
    () => Fetchers.getDashboardApiChartsTrackerList(params, client)
  )
}


