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
 * Get a paginated list of all user profiles
 *
 * @method GET
 * @path /profiles/profiles/
 */
export async function getProfilesProfiles(
  params?: { page?: number; page_size?: number },
  client?: API
): Promise<PaginatedUserProfileList> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesList(params?.page, params?.page_size)
  return PaginatedUserProfileListSchema.parse(response)
}

/**
 * Create user profile
 *
 * Create a new user profile
 *
 * @method POST
 * @path /profiles/profiles/
 */
export async function createProfilesProfiles(
  data: UserProfileRequest,
  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesCreate(data)
  return UserProfileSchema.parse(response)
}

/**
 * Get user profile
 *
 * Get detailed information about a specific user profile
 *
 * @method GET
 * @path /profiles/profiles/{id}/
 */
export async function getProfilesProfile(
  id: number,
  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesRetrieve(id)
  return UserProfileSchema.parse(response)
}

/**
 * Update user profile
 *
 * Update user profile information
 *
 * @method PUT
 * @path /profiles/profiles/{id}/
 */
export async function updateProfilesProfiles(
  id: number, data: UserProfileUpdateRequest,
  client?: API
): Promise<UserProfileUpdate> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesUpdate(id, data)
  return UserProfileUpdateSchema.parse(response)
}

/**
 * Partially update user profile
 *
 * Partially update user profile information
 *
 * @method PATCH
 * @path /profiles/profiles/{id}/
 */
export async function partialUpdateProfilesProfiles(
  id: number,
  client?: API
): Promise<UserProfileUpdate> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesPartialUpdate(id)
  return UserProfileUpdateSchema.parse(response)
}

/**
 * Delete user profile
 *
 * Delete a user profile
 *
 * @method DELETE
 * @path /profiles/profiles/{id}/
 */
export async function deleteProfilesProfiles(
  id: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesDestroy(id)
  return response
}

/**
 * Get my profile
 *
 * Get current user's profile
 *
 * @method GET
 * @path /profiles/profiles/me/
 */
export async function getProfilesProfilesMe(
  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesMeRetrieve()
  return UserProfileSchema.parse(response)
}

/**
 * Get my profile
 *
 * Get current user's profile
 *
 * @method PUT
 * @path /profiles/profiles/me/
 */
export async function updateProfilesProfilesMe(
  data: UserProfileRequest,
  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesMeUpdate(data)
  return UserProfileSchema.parse(response)
}

/**
 * Get my profile
 *
 * Get current user's profile
 *
 * @method PATCH
 * @path /profiles/profiles/me/
 */
export async function partialUpdateProfilesProfilesMe(
  client?: API
): Promise<UserProfile> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesMePartialUpdate()
  return UserProfileSchema.parse(response)
}

/**
 * Get profile statistics
 *
 * Get comprehensive profile statistics
 *
 * @method GET
 * @path /profiles/profiles/stats/
 */
export async function getProfilesProfilesStat(
  client?: API
): Promise<UserProfileStats> {
  const api = client || getAPIInstance()

  const response = await api.profiles_profiles.profilesStatsRetrieve()
  return UserProfileStatsSchema.parse(response)
}

