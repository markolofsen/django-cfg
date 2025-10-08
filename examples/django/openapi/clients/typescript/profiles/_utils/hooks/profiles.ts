/**
 * SWR Hooks for Profiles
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
import type { PaginatedUserProfileList } from '../schemas/PaginatedUserProfileList.schema'
import type { PatchedUserProfileRequest } from '../schemas/PatchedUserProfileRequest.schema'
import type { PatchedUserProfileUpdateRequest } from '../schemas/PatchedUserProfileUpdateRequest.schema'
import type { UserProfile } from '../schemas/UserProfile.schema'
import type { UserProfileRequest } from '../schemas/UserProfileRequest.schema'
import type { UserProfileStats } from '../schemas/UserProfileStats.schema'
import type { UserProfileUpdate } from '../schemas/UserProfileUpdate.schema'
import type { UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List user profiles
 *
 * @method GET
 * @path /profiles/profiles/
 */
export function useProfilesProfiles(params?: { page?: number; page_size?: number }) {
  return useSWR<PaginatedUserProfileList>(
    params ? ['profiles-profiles', params] : 'profiles-profiles',
    () => Fetchers.getProfilesProfiles(params)
  )
}

/**
 * Get user profile
 *
 * @method GET
 * @path /profiles/profiles/{id}/
 */
export function useProfilesProfile(id: number) {
  return useSWR<UserProfile>(
    ['profiles-profile', id],
    () => Fetchers.getProfilesProfile(id)
  )
}

/**
 * Get my profile
 *
 * @method GET
 * @path /profiles/profiles/me/
 */
export function useProfilesProfilesMe() {
  return useSWR<UserProfile>(
    'profiles-profiles-me',
    () => Fetchers.getProfilesProfilesMe()
  )
}

/**
 * Get profile statistics
 *
 * @method GET
 * @path /profiles/profiles/stats/
 */
export function useProfilesProfilesStat() {
  return useSWR<UserProfileStats>(
    'profiles-profiles-stat',
    () => Fetchers.getProfilesProfilesStat()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Create user profile
 *
 * @method POST
 * @path /profiles/profiles/
 */
export function useCreateProfilesProfiles() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileRequest): Promise<UserProfile> => {
    const result = await Fetchers.createProfilesProfiles(data)

    // Revalidate related queries
    mutate('profiles-profiles')

    return result
  }
}

/**
 * Update user profile
 *
 * @method PUT
 * @path /profiles/profiles/{id}/
 */
export function useUpdateProfilesProfiles() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: UserProfileUpdateRequest): Promise<UserProfileUpdate> => {
    const result = await Fetchers.updateProfilesProfiles(id, data)

    // Revalidate related queries
    mutate('profiles-profiles')
    mutate('profiles-profile')

    return result
  }
}

/**
 * Partially update user profile
 *
 * @method PATCH
 * @path /profiles/profiles/{id}/
 */
export function usePartialUpdateProfilesProfiles() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<UserProfileUpdate> => {
    const result = await Fetchers.partialUpdateProfilesProfiles(id)

    // Revalidate related queries
    mutate('profiles-profiles-partial')

    return result
  }
}

/**
 * Delete user profile
 *
 * @method DELETE
 * @path /profiles/profiles/{id}/
 */
export function useDeleteProfilesProfiles() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<void> => {
    const result = await Fetchers.deleteProfilesProfiles(id)

    // Revalidate related queries
    mutate('profiles-profiles')
    mutate('profiles-profile')

    return result
  }
}

/**
 * Get my profile
 *
 * @method PUT
 * @path /profiles/profiles/me/
 */
export function useUpdateProfilesProfilesMe() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileRequest): Promise<UserProfile> => {
    const result = await Fetchers.updateProfilesProfilesMe(data)

    // Revalidate related queries
    mutate('profiles-profiles-me')

    return result
  }
}

/**
 * Get my profile
 *
 * @method PATCH
 * @path /profiles/profiles/me/
 */
export function usePartialUpdateProfilesProfilesMe() {
  const { mutate } = useSWRConfig()

  return async (): Promise<UserProfile> => {
    const result = await Fetchers.partialUpdateProfilesProfilesMe()

    // Revalidate related queries
    mutate('profiles-profiles-me-partial')

    return result
  }
}
