/**
 * SWR Hooks for Endpoints
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
import * as Fetchers from '../fetchers/cfg__endpoints'
import type { API } from '../../index'
import type { EndpointsStatus } from '../schemas/EndpointsStatus.schema'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/endpoints/drf/
 */
export function useEndpointsDrfRetrieve(client?: API): ReturnType<typeof useSWR<EndpointsStatus>> {
  return useSWR<EndpointsStatus>(
    'cfg-endpoints-drf',
    () => Fetchers.getEndpointsDrfRetrieve(client)
  )
}


