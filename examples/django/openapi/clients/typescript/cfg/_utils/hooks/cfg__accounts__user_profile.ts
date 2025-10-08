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
 * @path /django_cfg_accounts/profile/
 */
export function useDjangoCfgAccountsProfile() {
  return useSWR<User>(
    'django-cfg-accounts-profile',
    () => Fetchers.getDjangoCfgAccountsProfile()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Upload user avatar
 *
 * @method POST
 * @path /django_cfg_accounts/profile/avatar/
 */
export function useCreateDjangoCfgAccountsProfileAvatar() {
  const { mutate } = useSWRConfig()

  return async (data: any): Promise<User> => {
    const result = await Fetchers.createDjangoCfgAccountsProfileAvatar(data)

    // Revalidate related queries
    mutate('django-cfg-accounts-profile-avatar')

    return result
  }
}

/**
 * Partial update user profile
 *
 * @method PUT
 * @path /django_cfg_accounts/profile/partial/
 */
export function usePartialUpdateDjangoCfgAccountsProfile() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileUpdateRequest): Promise<User> => {
    const result = await Fetchers.partialUpdateDjangoCfgAccountsProfile(data)

    // Revalidate related queries
    mutate('django-cfg-accounts-profile-partial')

    return result
  }
}

/**
 * Partial update user profile
 *
 * @method PATCH
 * @path /django_cfg_accounts/profile/partial/
 */
export function usePartialUpdateDjangoCfgAccountsProfilePartial() {
  const { mutate } = useSWRConfig()

  return async (): Promise<User> => {
    const result = await Fetchers.partialUpdateDjangoCfgAccountsProfilePartial()

    // Revalidate related queries
    mutate('django-cfg-accounts-profile-partial-partial')

    return result
  }
}

/**
 * Update user profile
 *
 * @method PUT
 * @path /django_cfg_accounts/profile/update/
 */
export function useUpdateDjangoCfgAccountsProfileUpdate() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileUpdateRequest): Promise<User> => {
    const result = await Fetchers.updateDjangoCfgAccountsProfileUpdate(data)

    // Revalidate related queries
    mutate('django-cfg-accounts-profile')

    return result
  }
}

/**
 * Update user profile
 *
 * @method PATCH
 * @path /django_cfg_accounts/profile/update/
 */
export function usePartialUpdateDjangoCfgAccountsProfileUpdate() {
  const { mutate } = useSWRConfig()

  return async (): Promise<User> => {
    const result = await Fetchers.partialUpdateDjangoCfgAccountsProfileUpdate()

    // Revalidate related queries
    mutate('django-cfg-accounts-profile-partial')

    return result
  }
}
