/**
 * SWR Hooks for Dashboard - Activity
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_activity'
import type { API } from '../../index'

/**
 * Get quick actions
 *
 * @method GET
 * @path /cfg/dashboard/api/activity/actions/
 */
export function useDashboardApiActivityActionsList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-dashboard-api-activity-actions',
    () => Fetchers.getDashboardApiActivityActionsList(client)
  )
}


/**
 * Get recent activity
 *
 * @method GET
 * @path /cfg/dashboard/api/activity/recent/
 */
export function useDashboardApiActivityRecentList(params?: { limit?: number }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-dashboard-api-activity-recent', params] : 'cfg-dashboard-api-activity-recent',
    () => Fetchers.getDashboardApiActivityRecentList(params, client)
  )
}


