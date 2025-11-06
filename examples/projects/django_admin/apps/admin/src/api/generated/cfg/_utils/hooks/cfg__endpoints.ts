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
import * as Fetchers from '../fetchers/cfg__endpoints'
import type { API } from '../../index'
import type { EndpointsStatus } from '../schemas/EndpointsStatus.schema'
import type { URLsList } from '../schemas/URLsList.schema'

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


/**
 * API operation
 *
 * @method GET
 * @path /cfg/endpoints/urls/
 */
export function useEndpointsUrlsRetrieve(client?: API): ReturnType<typeof useSWR<URLsList>> {
  return useSWR<URLsList>(
    'cfg-endpoints-url',
    () => Fetchers.getEndpointsUrlsRetrieve(client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/endpoints/urls/compact/
 */
export function useEndpointsUrlsCompactRetrieve(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-endpoints-urls-compact',
    () => Fetchers.getEndpointsUrlsCompactRetrieve(client)
  )
}


