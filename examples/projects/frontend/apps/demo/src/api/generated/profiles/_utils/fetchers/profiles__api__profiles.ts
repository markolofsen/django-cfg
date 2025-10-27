/**
 * Typed fetchers for Profiles
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { PaginatedUserProfileListSchema, type PaginatedUserProfileList } from '../schemas/PaginatedUserProfileList.schema'
import { PatchedUserProfileRequestSchema, type PatchedUserProfileRequest } from '../schemas/PatchedUserProfileRequest.schema'
import { PatchedUserProfileUpdateRequestSchema, type PatchedUserProfileUpdateRequest } from '../schemas/PatchedUserProfileUpdateRequest.schema'
import { UserProfileSchema, type UserProfile } from '../schemas/UserProfile.schema'
import { UserProfileRequestSchema, type UserProfileRequest } from '../schemas/UserProfileRequest.schema'
import { UserProfileStatsSchema, type UserProfileStats } from '../schemas/UserProfileStats.schema'
import { UserProfileUpdateSchema, type UserProfileUpdate } from '../schemas/UserProfileUpdate.schema'
import { UserProfileUpdateRequestSchema, type UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List user profiles
 *
 * @method GET
 * @path /api/profiles/profiles/
 */
export async function getProfilesProfilesList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedUserProfileList> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesList(params?.page, params?.page_size)
  return PaginatedUserProfileListSchema.parse(response)
}


/**
 * Create user profile
 *
 * @method POST
 * @path /api/profiles/profiles/
 */
export async function createProfilesProfilesCreate(  data: UserProfileRequest,  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesCreate(data)
  return UserProfileSchema.parse(response)
}


/**
 * Get user profile
 *
 * @method GET
 * @path /api/profiles/profiles/{id}/
 */
export async function getProfilesProfilesRetrieve(  id: number,  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesRetrieve(id)
  return UserProfileSchema.parse(response)
}


/**
 * Update user profile
 *
 * @method PUT
 * @path /api/profiles/profiles/{id}/
 */
export async function updateProfilesProfilesUpdate(  id: number, data: UserProfileUpdateRequest,  client?: API
): Promise<UserProfileUpdate> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesUpdate(id, data)
  return UserProfileUpdateSchema.parse(response)
}


/**
 * Partially update user profile
 *
 * @method PATCH
 * @path /api/profiles/profiles/{id}/
 */
export async function partialUpdateProfilesProfilesPartialUpdate(  id: number, data?: PatchedUserProfileUpdateRequest,  client?: API
): Promise<UserProfileUpdate> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesPartialUpdate(id, data)
  return UserProfileUpdateSchema.parse(response)
}


/**
 * Delete user profile
 *
 * @method DELETE
 * @path /api/profiles/profiles/{id}/
 */
export async function deleteProfilesProfilesDestroy(  id: number,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesDestroy(id)
  return response
}


/**
 * Get my profile
 *
 * @method GET
 * @path /api/profiles/profiles/me/
 */
export async function getProfilesProfilesMeRetrieve(  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesMeRetrieve()
  return UserProfileSchema.parse(response)
}


/**
 * Get my profile
 *
 * @method PUT
 * @path /api/profiles/profiles/me/
 */
export async function updateProfilesProfilesMeUpdate(  data: UserProfileRequest,  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesMeUpdate(data)
  return UserProfileSchema.parse(response)
}


/**
 * Get my profile
 *
 * @method PATCH
 * @path /api/profiles/profiles/me/
 */
export async function partialUpdateProfilesProfilesMePartialUpdate(  data?: PatchedUserProfileRequest,  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesMePartialUpdate(data)
  return UserProfileSchema.parse(response)
}


/**
 * Get profile statistics
 *
 * @method GET
 * @path /api/profiles/profiles/stats/
 */
export async function getProfilesProfilesStatsRetrieve(  client?: API
): Promise<UserProfileStats> {
  const api = client || getAPIInstance()
  const response = await api.profiles_profiles.profilesStatsRetrieve()
  return UserProfileStatsSchema.parse(response)
}


