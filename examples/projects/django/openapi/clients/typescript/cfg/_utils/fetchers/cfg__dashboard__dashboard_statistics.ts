/**
 * Typed fetchers for Dashboard - Statistics
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
import { UserStatisticsSchema, type UserStatistics } from '../schemas/UserStatistics.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get application statistics
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/apps/
 */
export async function getDashboardApiStatisticsAppsList(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_statistics.dashboardApiStatisticsAppsList()
  return response
}


/**
 * Get statistics cards
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/cards/
 */
export async function getDashboardApiStatisticsCardsList(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_statistics.dashboardApiStatisticsCardsList()
  return response
}


/**
 * Get user statistics
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/users/
 */
export async function getDashboardApiStatisticsUsersRetrieve(  client?: any
): Promise<UserStatistics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_statistics.dashboardApiStatisticsUsersRetrieve()
  return UserStatisticsSchema.parse(response)
}


