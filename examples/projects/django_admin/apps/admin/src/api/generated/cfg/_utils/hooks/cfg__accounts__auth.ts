/**
 * SWR Hooks for Auth
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
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__accounts__auth'
import type { API } from '../../index'
import type { TokenRefresh } from '../schemas/TokenRefresh.schema'
import type { TokenRefreshRequest } from '../schemas/TokenRefreshRequest.schema'

/**
 * API operation
 *
 * @method POST
 * @path /cfg/accounts/token/refresh/
 */
export function useCreateAccountsTokenRefreshCreate() {
  const { mutate } = useSWRConfig()

  return async (data: TokenRefreshRequest, client?: API): Promise<TokenRefresh> => {
    const result = await Fetchers.createAccountsTokenRefreshCreate(data, client)
    // Revalidate related queries
    mutate('cfg-accounts-token-refresh')
    return result
  }
}


