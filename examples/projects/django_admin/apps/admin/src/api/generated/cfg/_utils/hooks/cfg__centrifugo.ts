/**
 * SWR Hooks for Centrifugo
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
import * as Fetchers from '../fetchers/cfg__centrifugo'
import type { API } from '../../index'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/channels/
 */
export function useCentrifugoMonitorChannelsRetrieve(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-centrifugo-monitor-channel',
    () => Fetchers.getCentrifugoMonitorChannelsRetrieve(client)
  )
}


