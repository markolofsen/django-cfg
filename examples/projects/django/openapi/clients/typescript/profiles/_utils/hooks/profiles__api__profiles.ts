/**
 * SWR Hooks for Profiles
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
import * as Fetchers from '../fetchers/profiles__api__profiles'
import type { API } from '../../index'
import type { PaginatedUserProfileList } from '../schemas/PaginatedUserProfileList.schema'
import type { PatchedUserProfileRequest } from '../schemas/PatchedUserProfileRequest.schema'
import type { PatchedUserProfileUpdateRequest } from '../schemas/PatchedUserProfileUpdateRequest.schema'
import type { UserProfile } from '../schemas/UserProfile.schema'
import type { UserProfileRequest } from '../schemas/UserProfileRequest.schema'
import type { UserProfileStats } from '../schemas/UserProfileStats.schema'
import type { UserProfileUpdate } from '../schemas/UserProfileUpdate.schema'
import type { UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'

/**
 * List user profiles
 *
 * @method GET
 * @path /api/profiles/profiles/
 */
export function useProfilesProfilesList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedUserProfileList>> {
  return useSWR<PaginatedUserProfileList>(
    params ? ['profiles-profiles', params] : 'profiles-profiles',
    () => Fetchers.getProfilesProfilesList(params, client)
  )
}


/**
 * Create user profile
 *
 * @method POST
 * @path /api/profiles/profiles/
 */
export function useCreateProfilesProfilesCreate() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileRequest, client?: API): Promise<UserProfile> => {
    const result = await Fetchers.createProfilesProfilesCreate(data, client)
    // Revalidate related queries
    mutate('profiles-profiles')
    return result
  }
}


/**
 * Get user profile
 *
 * @method GET
 * @path /api/profiles/profiles/{id}/
 */
export function useProfilesProfilesRetrieve(id: number, client?: API): ReturnType<typeof useSWR<UserProfile>> {
  return useSWR<UserProfile>(
    ['profiles-profile', id],
    () => Fetchers.getProfilesProfilesRetrieve(id, client)
  )
}


/**
 * Update user profile
 *
 * @method PUT
 * @path /api/profiles/profiles/{id}/
 */
export function useUpdateProfilesProfilesUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: UserProfileUpdateRequest, client?: API): Promise<UserProfileUpdate> => {
    const result = await Fetchers.updateProfilesProfilesUpdate(id, data, client)
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
 * @path /api/profiles/profiles/{id}/
 */
export function usePartialUpdateProfilesProfilesPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data?: PatchedUserProfileUpdateRequest, client?: API): Promise<UserProfileUpdate> => {
    const result = await Fetchers.partialUpdateProfilesProfilesPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('profiles-profiles-partial')
    return result
  }
}


/**
 * Delete user profile
 *
 * @method DELETE
 * @path /api/profiles/profiles/{id}/
 */
export function useDeleteProfilesProfilesDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: number, client?: API): Promise<void> => {
    const result = await Fetchers.deleteProfilesProfilesDestroy(id, client)
    // Revalidate related queries
    mutate('profiles-profiles')
    mutate('profiles-profile')
    return result
  }
}


/**
 * Get my profile
 *
 * @method GET
 * @path /api/profiles/profiles/me/
 */
export function useProfilesProfilesMeRetrieve(client?: API): ReturnType<typeof useSWR<UserProfile>> {
  return useSWR<UserProfile>(
    'profiles-profiles-me',
    () => Fetchers.getProfilesProfilesMeRetrieve(client)
  )
}


/**
 * Get my profile
 *
 * @method PUT
 * @path /api/profiles/profiles/me/
 */
export function useUpdateProfilesProfilesMeUpdate() {
  const { mutate } = useSWRConfig()

  return async (data: UserProfileRequest, client?: API): Promise<UserProfile> => {
    const result = await Fetchers.updateProfilesProfilesMeUpdate(data, client)
    // Revalidate related queries
    mutate('profiles-profiles-me')
    return result
  }
}


/**
 * Get my profile
 *
 * @method PATCH
 * @path /api/profiles/profiles/me/
 */
export function usePartialUpdateProfilesProfilesMePartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (data?: PatchedUserProfileRequest, client?: API): Promise<UserProfile> => {
    const result = await Fetchers.partialUpdateProfilesProfilesMePartialUpdate(data, client)
    // Revalidate related queries
    mutate('profiles-profiles-me-partial')
    return result
  }
}


/**
 * Get profile statistics
 *
 * @method GET
 * @path /api/profiles/profiles/stats/
 */
export function useProfilesProfilesStatsRetrieve(client?: API): ReturnType<typeof useSWR<UserProfileStats>> {
  return useSWR<UserProfileStats>(
    'profiles-profiles-stat',
    () => Fetchers.getProfilesProfilesStatsRetrieve(client)
  )
}


