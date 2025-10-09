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
 * @path /cfg/accounts/profile/
 */
export async function getCfgAccountsProfileById(
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.cfgAccountsProfileRetrieve()
  return UserSchema.parse(response)
}

/**
 * Upload user avatar
 *
 * Upload avatar image for the current authenticated user. Accepts multipart/form-data with 'avatar' field.
 *
 * @method POST
 * @path /cfg/accounts/profile/avatar/
 */
export async function createCfgAccountsProfileAvatar(
  data: any,
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.cfgAccountsProfileAvatarCreate(data)
  return UserSchema.parse(response)
}

/**
 * Partial update user profile
 *
 * Partially update the current authenticated user's profile information. Supports avatar upload.
 *
 * @method PUT
 * @path /cfg/accounts/profile/partial/
 */
export async function partialUpdateCfgAccountsProfile(
  data: UserProfileUpdateRequest,
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.cfgAccountsProfilePartialUpdate(data)
  return UserSchema.parse(response)
}

/**
 * Partial update user profile
 *
 * Partially update the current authenticated user's profile information. Supports avatar upload.
 *
 * @method PATCH
 * @path /cfg/accounts/profile/partial/
 */
export async function partialUpdateCfgAccountsProfilePartial(
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.cfgAccountsProfilePartialPartialUpdate()
  return UserSchema.parse(response)
}

/**
 * Update user profile
 *
 * Update the current authenticated user's profile information.
 *
 * @method PUT
 * @path /cfg/accounts/profile/update/
 */
export async function updateCfgAccountsProfileUpdate(
  data: UserProfileUpdateRequest,
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.cfgAccountsProfileUpdateUpdate(data)
  return UserSchema.parse(response)
}

/**
 * Update user profile
 *
 * Update the current authenticated user's profile information.
 *
 * @method PATCH
 * @path /cfg/accounts/profile/update/
 */
export async function partialUpdateCfgAccountsProfileUpdate(
  client?: API
): Promise<User> {
  const api = client || getAPIInstance()

  const response = await api.cfg_user_profile.cfgAccountsProfileUpdatePartialUpdate()
  return UserSchema.parse(response)
}

