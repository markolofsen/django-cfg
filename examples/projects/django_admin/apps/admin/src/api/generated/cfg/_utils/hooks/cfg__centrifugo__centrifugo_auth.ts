/**
 * SWR Hooks for Centrifugo Auth
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
import * as Fetchers from '../fetchers/cfg__centrifugo__centrifugo_auth'
import type { API } from '../../index'
import type { ConnectionTokenResponse } from '../schemas/ConnectionTokenResponse.schema'

/**
 * Get Centrifugo connection token
 *
 * @method GET
 * @path /cfg/centrifugo/auth/token/
 */
export function useCentrifugoAuthTokenRetrieve(client?: API): ReturnType<typeof useSWR<ConnectionTokenResponse>> {
  return useSWR<ConnectionTokenResponse>(
    'cfg-centrifugo-auth-token',
    () => Fetchers.getCentrifugoAuthTokenRetrieve(client)
  )
}


