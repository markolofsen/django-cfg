/**
 * SWR Hooks for Auth
 *
 * Auto-generated React hooks for data fetching with SWR.
 *
 * Setup:
 * ```typescript
 * // Configure API once (in your app root)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 * ```
 *
 * Usage:
 * ```typescript
 * // Query hook
 * const { data, error, mutate } = useShopProducts({ page: 1 })
 *
 * // Mutation hook
 * const createProduct = useCreateShopProduct()
 * await createProduct({ name: 'Product', price: 99 })
 * ```
 */
import type { TokenRefresh } from '../schemas/TokenRefresh.schema'
import type { TokenRefreshRequest } from '../schemas/TokenRefreshRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /cfg/accounts/token/refresh/
 */
export function useCreateCfgAccountsTokenRefresh() {
  const { mutate } = useSWRConfig()

  return async (data: TokenRefreshRequest): Promise<TokenRefresh> => {
    const result = await Fetchers.createCfgAccountsTokenRefresh(data)

    // Revalidate related queries
    mutate('cfg-accounts-token-refresh')

    return result
  }
}
