/**
 * SWR Hooks for User Profile
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
import type { PatchedUserProfileUpdateRequest } from '../schemas/PatchedUserProfileUpdateRequest.schema'
import type { User } from '../schemas/User.schema'
import type { UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * Get current user profile
 *
 * @method GET
 * @path /cfg/accounts/profile/
 */
export function useCfgAccountsProfileById() {
  return useSWR<User>(
    'cfg-accounts-profile',
    () => Fetchers.getCfgAccountsProfileById()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Upload user avatar
 *
 * @method POST
 * @path /cfg/accounts/profile/avatar/
 */
export function useCreateCfgAccountsProfileAvatar() {
  const { mutate } = useSWRConfig()

  return async (data: any): Promise<User> => {
    const result = await Fetchers.createCfgAccountsProfileAvatar(data)

    // Revalidate related queries
    mutate('cfg-accounts-profile-avatar')

    return result
  }
}

/**
 * Partial update user profile
 *
 * @method PUT
 * @path /cfg/accounts/profile/partial/
 */
export function usePartialUpdateCfgAccountsProfile() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileUpdateRequest): Promise<User> => {
    const result = await Fetchers.partialUpdateCfgAccountsProfile(data)

    // Revalidate related queries
    mutate('cfg-accounts-profile-partial')

    return result
  }
}

/**
 * Partial update user profile
 *
 * @method PATCH
 * @path /cfg/accounts/profile/partial/
 */
export function usePartialUpdateCfgAccountsProfilePartial() {
  const { mutate } = useSWRConfig()

  return async (): Promise<User> => {
    const result = await Fetchers.partialUpdateCfgAccountsProfilePartial()

    // Revalidate related queries
    mutate('cfg-accounts-profile-partial-partial')

    return result
  }
}

/**
 * Update user profile
 *
 * @method PUT
 * @path /cfg/accounts/profile/update/
 */
export function useUpdateCfgAccountsProfileUpdate() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileUpdateRequest): Promise<User> => {
    const result = await Fetchers.updateCfgAccountsProfileUpdate(data)

    // Revalidate related queries
    mutate('cfg-accounts-profile')

    return result
  }
}

/**
 * Update user profile
 *
 * @method PATCH
 * @path /cfg/accounts/profile/update/
 */
export function usePartialUpdateCfgAccountsProfileUpdate() {
  const { mutate } = useSWRConfig()

  return async (): Promise<User> => {
    const result = await Fetchers.partialUpdateCfgAccountsProfileUpdate()

    // Revalidate related queries
    mutate('cfg-accounts-profile-partial')

    return result
  }
}
