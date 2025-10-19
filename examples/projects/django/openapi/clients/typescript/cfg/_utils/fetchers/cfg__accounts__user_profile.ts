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
import { PatchedUserProfileUpdateRequestSchema, type PatchedUserProfileUpdateRequest } from '../schemas/PatchedUserProfileUpdateRequest.schema'
import { UserSchema, type User } from '../schemas/User.schema'
import { UserProfileUpdateRequestSchema, type UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Get current user profile
 *
 * @method GET
 * @path /cfg/accounts/profile/
 */
export async function getAccountsProfileRetrieve(  client?
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileRetrieve()
  return UserSchema.parse(response)
}


/**
 * Upload user avatar
 *
 * @method POST
 * @path /cfg/accounts/profile/avatar/
 */
export async function createAccountsProfileAvatarCreate(  data: any,  client?
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileAvatarCreate(data)
  return UserSchema.parse(response)
}


/**
 * Partial update user profile
 *
 * @method PUT
 * @path /cfg/accounts/profile/partial/
 */
export async function partialUpdateAccountsProfilePartialUpdate(  data: UserProfileUpdateRequest,  client?
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfilePartialUpdate(data)
  return UserSchema.parse(response)
}


/**
 * Partial update user profile
 *
 * @method PATCH
 * @path /cfg/accounts/profile/partial/
 */
export async function partialUpdateAccountsProfilePartialPartialUpdate(  data?: PatchedUserProfileUpdateRequest,  client?
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfilePartialPartialUpdate(data)
  return UserSchema.parse(response)
}


/**
 * Update user profile
 *
 * @method PUT
 * @path /cfg/accounts/profile/update/
 */
export async function updateAccountsProfileUpdateUpdate(  data: UserProfileUpdateRequest,  client?
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileUpdateUpdate(data)
  return UserSchema.parse(response)
}


/**
 * Update user profile
 *
 * @method PATCH
 * @path /cfg/accounts/profile/update/
 */
export async function partialUpdateAccountsProfileUpdatePartialUpdate(  data?: PatchedUserProfileUpdateRequest,  client?
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileUpdatePartialUpdate(data)
  return UserSchema.parse(response)
}


