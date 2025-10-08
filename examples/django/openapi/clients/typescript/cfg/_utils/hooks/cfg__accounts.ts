/**
 * SWR Hooks for Accounts
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
import type { OTPRequestRequest } from '../schemas/OTPRequestRequest.schema'
import type { OTPRequestResponse } from '../schemas/OTPRequestResponse.schema'
import type { OTPVerifyRequest } from '../schemas/OTPVerifyRequest.schema'
import type { OTPVerifyResponse } from '../schemas/OTPVerifyResponse.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /django_cfg_accounts/otp/request/
 */
export function useCreateDjangoCfgAccountsOtpRequest() {
  const { mutate } = useSWRConfig()

  return async (data: OTPRequestRequest): Promise<OTPRequestResponse> => {
    const result = await Fetchers.createDjangoCfgAccountsOtpRequest(data)

    // Revalidate related queries
    mutate('django-cfg-accounts-otp-request')

    return result
  }
}

/**
 *
 * @method POST
 * @path /django_cfg_accounts/otp/verify/
 */
export function useCreateDjangoCfgAccountsOtpVerify() {
  const { mutate } = useSWRConfig()

  return async (data: OTPVerifyRequest): Promise<OTPVerifyResponse> => {
    const result = await Fetchers.createDjangoCfgAccountsOtpVerify(data)

    // Revalidate related queries
    mutate('django-cfg-accounts-otp-verify')

    return result
  }
}
