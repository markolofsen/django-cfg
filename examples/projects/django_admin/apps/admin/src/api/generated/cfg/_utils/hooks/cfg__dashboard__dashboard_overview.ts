/**
 * SWR Hooks for Dashboard - Overview
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_overview'
import type { API } from '../../index'
import type { DashboardOverview } from '../schemas/DashboardOverview.schema'

/**
 * Get dashboard overview
 *
 * @method GET
 * @path /cfg/dashboard/api/overview/overview/
 */
export function useDashboardApiOverviewOverviewRetrieve(client?: API): ReturnType<typeof useSWR<DashboardOverview>> {
  return useSWR<DashboardOverview>(
    'cfg-dashboard-api-overview-overview',
    () => Fetchers.getDashboardApiOverviewOverviewRetrieve(client)
  )
}


