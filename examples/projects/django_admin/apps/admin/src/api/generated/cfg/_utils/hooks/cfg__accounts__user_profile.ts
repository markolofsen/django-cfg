/**
 * SWR Hooks for User Profile
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
import * as Fetchers from '../fetchers/cfg__accounts__user_profile'
import type { API } from '../../index'
import type { PatchedUserProfileUpdateRequest } from '../schemas/PatchedUserProfileUpdateRequest.schema'
import type { User } from '../schemas/User.schema'
import type { UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'

/**
 * Get current user profile
 *
 * @method GET
 * @path /cfg/accounts/profile/
 */
export function useAccountsProfileRetrieve(client?: API): ReturnType<typeof useSWR<User>> {
  return useSWR<User>(
    'cfg-accounts-profile',
    () => Fetchers.getAccountsProfileRetrieve(client)
  )
}


/**
 * Upload user avatar
 *
 * @method POST
 * @path /cfg/accounts/profile/avatar/
 */
export function useCreateAccountsProfileAvatarCreate() {
  const { mutate } = useSWRConfig()

  return async (data: any, client?: API): Promise<User> => {
    const result = await Fetchers.createAccountsProfileAvatarCreate(data, client)
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
export function usePartialUpdateAccountsProfilePartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileUpdateRequest, client?: API): Promise<User> => {
    const result = await Fetchers.partialUpdateAccountsProfilePartialUpdate(data, client)
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
export function usePartialUpdateAccountsProfilePartialPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (data?: PatchedUserProfileUpdateRequest, client?: API): Promise<User> => {
    const result = await Fetchers.partialUpdateAccountsProfilePartialPartialUpdate(data, client)
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
export function useUpdateAccountsProfileUpdateUpdate() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileUpdateRequest, client?: API): Promise<User> => {
    const result = await Fetchers.updateAccountsProfileUpdateUpdate(data, client)
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
export function usePartialUpdateAccountsProfileUpdatePartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (data?: PatchedUserProfileUpdateRequest, client?: API): Promise<User> => {
    const result = await Fetchers.partialUpdateAccountsProfileUpdatePartialUpdate(data, client)
    // Revalidate related queries
    mutate('cfg-accounts-profile-partial')
    return result
  }
}


