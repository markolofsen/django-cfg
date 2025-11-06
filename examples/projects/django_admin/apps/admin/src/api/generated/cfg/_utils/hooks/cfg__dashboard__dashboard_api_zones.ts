/**
 * SWR Hooks for Dashboard - API Zones
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_api_zones'
import type { API } from '../../index'
import type { APIZonesSummary } from '../schemas/APIZonesSummary.schema'

/**
 * Get all API zones
 *
 * @method GET
 * @path /cfg/dashboard/api/zones/
 */
export function useDashboardApiZonesList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-dashboard-api-zones',
    () => Fetchers.getDashboardApiZonesList(client)
  )
}


/**
 * Get zones summary
 *
 * @method GET
 * @path /cfg/dashboard/api/zones/summary/
 */
export function useDashboardApiZonesSummaryRetrieve(client?: API): ReturnType<typeof useSWR<APIZonesSummary>> {
  return useSWR<APIZonesSummary>(
    'cfg-dashboard-api-zones-summary',
    () => Fetchers.getDashboardApiZonesSummaryRetrieve(client)
  )
}


