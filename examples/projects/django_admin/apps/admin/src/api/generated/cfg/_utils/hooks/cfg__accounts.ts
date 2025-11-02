/**
 * SWR Hooks for Accounts
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
import * as Fetchers from '../fetchers/cfg__accounts'
import type { API } from '../../index'
import type { OTPRequestRequest } from '../schemas/OTPRequestRequest.schema'
import type { OTPRequestResponse } from '../schemas/OTPRequestResponse.schema'
import type { OTPVerifyRequest } from '../schemas/OTPVerifyRequest.schema'
import type { OTPVerifyResponse } from '../schemas/OTPVerifyResponse.schema'

/**
 * API operation
 *
 * @method POST
 * @path /cfg/accounts/otp/request/
 */
export function useCreateAccountsOtpRequestCreate() {
  const { mutate } = useSWRConfig()

  return async (data: OTPRequestRequest, client?: API): Promise<OTPRequestResponse> => {
    const result = await Fetchers.createAccountsOtpRequestCreate(data, client)
    // Revalidate related queries
    mutate('cfg-accounts-otp-request')
    return result
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/accounts/otp/verify/
 */
export function useCreateAccountsOtpVerifyCreate() {
  const { mutate } = useSWRConfig()

  return async (data: OTPVerifyRequest, client?: API): Promise<OTPVerifyResponse> => {
    const result = await Fetchers.createAccountsOtpVerifyCreate(data, client)
    // Revalidate related queries
    mutate('cfg-accounts-otp-verify')
    return result
  }
}


