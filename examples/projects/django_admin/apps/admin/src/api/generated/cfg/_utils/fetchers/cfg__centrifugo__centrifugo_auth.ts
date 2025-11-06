/**
 * Typed fetchers for Centrifugo Auth
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
import { ConnectionTokenResponseSchema, type ConnectionTokenResponse } from '../schemas/ConnectionTokenResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get Centrifugo connection token
 *
 * @method GET
 * @path /cfg/centrifugo/auth/token/
 */
export async function getCentrifugoAuthTokenRetrieve(  client?: any
): Promise<ConnectionTokenResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_auth.tokenRetrieve()
  return ConnectionTokenResponseSchema.parse(response)
}


