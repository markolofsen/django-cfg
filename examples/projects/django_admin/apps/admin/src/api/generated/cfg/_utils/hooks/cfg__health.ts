/**
 * SWR Hooks for Health
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
import * as Fetchers from '../fetchers/cfg__health'
import type { API } from '../../index'
import type { HealthCheck } from '../schemas/HealthCheck.schema'
import type { QuickHealth } from '../schemas/QuickHealth.schema'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/health/drf/
 */
export function useHealthDrfRetrieve(client?: API): ReturnType<typeof useSWR<HealthCheck>> {
  return useSWR<HealthCheck>(
    'cfg-health-drf',
    () => Fetchers.getHealthDrfRetrieve(client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/health/drf/quick/
 */
export function useHealthDrfQuickRetrieve(client?: API): ReturnType<typeof useSWR<QuickHealth>> {
  return useSWR<QuickHealth>(
    'cfg-health-drf-quick',
    () => Fetchers.getHealthDrfQuickRetrieve(client)
  )
}


