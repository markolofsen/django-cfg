/**
 * SWR Hooks for Dashboard - Statistics
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_statistics'
import type { API } from '../../index'
import type { UserStatistics } from '../schemas/UserStatistics.schema'

/**
 * Get application statistics
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/apps/
 */
export function useDashboardApiStatisticsAppsList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-dashboard-api-statistics-apps',
    () => Fetchers.getDashboardApiStatisticsAppsList(client)
  )
}


/**
 * Get statistics cards
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/cards/
 */
export function useDashboardApiStatisticsCardsList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-dashboard-api-statistics-cards',
    () => Fetchers.getDashboardApiStatisticsCardsList(client)
  )
}


/**
 * Get user statistics
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/users/
 */
export function useDashboardApiStatisticsUsersRetrieve(client?: API): ReturnType<typeof useSWR<UserStatistics>> {
  return useSWR<UserStatistics>(
    'cfg-dashboard-api-statistics-user',
    () => Fetchers.getDashboardApiStatisticsUsersRetrieve(client)
  )
}


