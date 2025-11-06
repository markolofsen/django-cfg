/**
 * Typed fetchers for Grpc Api Keys
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
import { ApiKeySchema, type ApiKey } from '../schemas/ApiKey.schema'
import { ApiKeyStatsSchema, type ApiKeyStats } from '../schemas/ApiKeyStats.schema'
import { PaginatedApiKeyListSchema, type PaginatedApiKeyList } from '../schemas/PaginatedApiKeyList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List API keys
 *
 * @method GET
 * @path /cfg/grpc/api-keys/
 */
export async function getGrpcApiKeysList(  params?: { is_active?: boolean; key_type?: string; page?: number; page_size?: number; user_id?: number },  client?: any
): Promise<PaginatedApiKeyList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_api_keys.list(params?.is_active, params?.key_type, params?.page, params?.page_size, params?.user_id)
  return PaginatedApiKeyListSchema.parse(response)
}


/**
 * Get API key details
 *
 * @method GET
 * @path /cfg/grpc/api-keys/{id}/
 */
export async function getGrpcApiKeysRetrieve(  id: number,  client?: any
): Promise<ApiKey> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_api_keys.retrieve(id)
  return ApiKeySchema.parse(response)
}


/**
 * Get API keys statistics
 *
 * @method GET
 * @path /cfg/grpc/api-keys/stats/
 */
export async function getGrpcApiKeysStatsRetrieve(  client?: any
): Promise<ApiKeyStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_api_keys.statsRetrieve()
  return ApiKeyStatsSchema.parse(response)
}


