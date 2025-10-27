/**
 * Typed fetchers for Dashboard - Charts
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
import { ChartDataSchema, type ChartData } from '../schemas/ChartData.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Get user activity chart
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/activity/
 */
export async function getDashboardApiChartsActivityRetrieve(  params?: { days?: number },  client?: API
): Promise<ChartData> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_charts.dashboardApiChartsActivityRetrieve(params?.days)
  return ChartDataSchema.parse(response)
}


/**
 * Get recent users
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/recent-users/
 */
export async function getDashboardApiChartsRecentUsersList(  params?: { limit?: number },  client?: API
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_charts.dashboardApiChartsRecentUsersList(params?.limit)
  return response
}


/**
 * Get user registration chart
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/registrations/
 */
export async function getDashboardApiChartsRegistrationsRetrieve(  params?: { days?: number },  client?: API
): Promise<ChartData> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_charts.dashboardApiChartsRegistrationsRetrieve(params?.days)
  return ChartDataSchema.parse(response)
}


/**
 * Get activity tracker
 *
 * @method GET
 * @path /cfg/dashboard/api/charts/tracker/
 */
export async function getDashboardApiChartsTrackerList(  params?: { weeks?: number },  client?: API
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_charts.dashboardApiChartsTrackerList(params?.weeks)
  return response
}


