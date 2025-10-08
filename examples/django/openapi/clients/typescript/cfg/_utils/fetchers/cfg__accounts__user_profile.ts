/**
 * Typed fetchers for User Profile
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
import { UserSchema, type User } from '../schemas/User.schema'
import { UserProfileUpdateRequestSchema, type UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Get current user profile
 *
 * Retrieve the current authenticated user's profile information.
 *
 * @method GET
 * @path /django_cfg_accounts/profile/
 */
export async function getDjangoCfgAccountsProfile(
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.profileRetrieve()
  return UserSchema.parse(response)
}

/**
 * Upload user avatar
 *
 * Upload avatar image for the current authenticated user. Accepts multipart/form-data with 'avatar' field.
 *
 * @method POST
 * @path /django_cfg_accounts/profile/avatar/
 */
export async function createDjangoCfgAccountsProfileAvatar(
  data: any,
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.profileAvatarCreate(data)
  return UserSchema.parse(response)
}

/**
 * Partial update user profile
 *
 * Partially update the current authenticated user's profile information. Supports avatar upload.
 *
 * @method PUT
 * @path /django_cfg_accounts/profile/partial/
 */
export async function partialUpdateDjangoCfgAccountsProfile(
  data: UserProfileUpdateRequest,
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.profilePartialUpdate(data)
  return UserSchema.parse(response)
}

/**
 * Partial update user profile
 *
 * Partially update the current authenticated user's profile information. Supports avatar upload.
 *
 * @method PATCH
 * @path /django_cfg_accounts/profile/partial/
 */
export async function partialUpdateDjangoCfgAccountsProfilePartial(
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.profilePartialPartialUpdate()
  return UserSchema.parse(response)
}

/**
 * Update user profile
 *
 * Update the current authenticated user's profile information.
 *
 * @method PUT
 * @path /django_cfg_accounts/profile/update/
 */
export async function updateDjangoCfgAccountsProfileUpdate(
  data: UserProfileUpdateRequest,
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.profileUpdateUpdate(data)
  return UserSchema.parse(response)
}

/**
 * Update user profile
 *
 * Update the current authenticated user's profile information.
 *
 * @method PATCH
 * @path /django_cfg_accounts/profile/update/
 */
export async function partialUpdateDjangoCfgAccountsProfileUpdate(
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.profileUpdatePartialUpdate()
  return UserSchema.parse(response)
}

