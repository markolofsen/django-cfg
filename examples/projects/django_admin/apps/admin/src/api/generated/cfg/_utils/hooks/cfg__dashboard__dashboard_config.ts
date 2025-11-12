/**
 * SWR Hooks for Dashboard - Config
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_config'
import type { API } from '../../index'
import type { ConfigData } from '../schemas/ConfigData.schema'

/**
 * Get configuration data
 *
 * @method GET
 * @path /cfg/dashboard/api/config/config/
 */
export function useDashboardApiConfigConfigRetrieve(client?: API): ReturnType<typeof useSWR<ConfigData>> {
  return useSWR<ConfigData>(
    'cfg-dashboard-api-config-config',
    () => Fetchers.getDashboardApiConfigConfigRetrieve(client)
  )
}


