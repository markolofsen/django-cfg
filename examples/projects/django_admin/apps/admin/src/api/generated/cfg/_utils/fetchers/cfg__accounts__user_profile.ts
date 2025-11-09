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
import { consola } from 'consola'
import { PatchedUserProfileUpdateRequestSchema, type PatchedUserProfileUpdateRequest } from '../schemas/PatchedUserProfileUpdateRequest.schema'
import { UserSchema, type User } from '../schemas/User.schema'
import { UserProfileUpdateRequestSchema, type UserProfileUpdateRequest } from '../schemas/UserProfileUpdateRequest.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get current user profile
 *
 * @method GET
 * @path /cfg/accounts/profile/
 */
export async function getAccountsProfileRetrieve(  client?: any
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileRetrieve()
  try {
    return UserSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getAccountsProfileRetrieve',
      message: `Path: /cfg/accounts/profile/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Upload user avatar
 *
 * @method POST
 * @path /cfg/accounts/profile/avatar/
 */
export async function createAccountsProfileAvatarCreate(  data: any,  client?: any
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileAvatarCreate(data)
  try {
    return UserSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createAccountsProfileAvatarCreate',
      message: `Path: /cfg/accounts/profile/avatar/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Partial update user profile
 *
 * @method PUT
 * @path /cfg/accounts/profile/partial/
 */
export async function partialUpdateAccountsProfilePartialUpdate(  data: UserProfileUpdateRequest,  client?: any
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfilePartialUpdate(data)
  try {
    return UserSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateAccountsProfilePartialUpdate',
      message: `Path: /cfg/accounts/profile/partial/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Partial update user profile
 *
 * @method PATCH
 * @path /cfg/accounts/profile/partial/
 */
export async function partialUpdateAccountsProfilePartialPartialUpdate(  data?: PatchedUserProfileUpdateRequest,  client?: any
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfilePartialPartialUpdate(data)
  try {
    return UserSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateAccountsProfilePartialPartialUpdate',
      message: `Path: /cfg/accounts/profile/partial/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Update user profile
 *
 * @method PUT
 * @path /cfg/accounts/profile/update/
 */
export async function updateAccountsProfileUpdateUpdate(  data: UserProfileUpdateRequest,  client?: any
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileUpdateUpdate(data)
  try {
    return UserSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateAccountsProfileUpdateUpdate',
      message: `Path: /cfg/accounts/profile/update/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Update user profile
 *
 * @method PATCH
 * @path /cfg/accounts/profile/update/
 */
export async function partialUpdateAccountsProfileUpdatePartialUpdate(  data?: PatchedUserProfileUpdateRequest,  client?: any
): Promise<User> {
  const api = client || getAPIInstance()
  const response = await api.cfg_user_profile.accountsProfileUpdatePartialUpdate(data)
  try {
    return UserSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateAccountsProfileUpdatePartialUpdate',
      message: `Path: /cfg/accounts/profile/update/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


