/**
 * Typed fetchers for Cfg Accounts
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
import { OTPRequestRequestSchema, type OTPRequestRequest } from '../schemas/OTPRequestRequest.schema'
import { OTPRequestResponseSchema, type OTPRequestResponse } from '../schemas/OTPRequestResponse.schema'
import { OTPVerifyRequestSchema, type OTPVerifyRequest } from '../schemas/OTPVerifyRequest.schema'
import { OTPVerifyResponseSchema, type OTPVerifyResponse } from '../schemas/OTPVerifyResponse.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * createCfgAccountsOtpRequest
 *
 * Request OTP code to email or phone.
 *
 * @method POST
 * @path /cfg/accounts/otp/request/
 */
export async function createCfgAccountsOtpRequest(
  data: OTPRequestRequest,
  client?: API
): Promise<OTPRequestResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__accounts.cfgAccountsOtpRequestCreate(data)
  return OTPRequestResponseSchema.parse(response)
}

/**
 * createCfgAccountsOtpVerify
 *
 * Verify OTP code and return JWT tokens.
 *
 * @method POST
 * @path /cfg/accounts/otp/verify/
 */
export async function createCfgAccountsOtpVerify(
  data: OTPVerifyRequest,
  client?: API
): Promise<OTPVerifyResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__accounts.cfgAccountsOtpVerifyCreate(data)
  return OTPVerifyResponseSchema.parse(response)
}

