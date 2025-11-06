/**
 * SWR Hooks for Grpc Api Keys
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
import * as Fetchers from '../fetchers/cfg__grpc__grpc_api_keys'
import type { API } from '../../index'
import type { ApiKey } from '../schemas/ApiKey.schema'
import type { ApiKeyStats } from '../schemas/ApiKeyStats.schema'
import type { PaginatedApiKeyList } from '../schemas/PaginatedApiKeyList.schema'

/**
 * List API keys
 *
 * @method GET
 * @path /cfg/grpc/api-keys/
 */
export function useGrpcApiKeysList(params?: { is_active?: boolean; key_type?: string; page?: number; page_size?: number; user_id?: number }, client?: API): ReturnType<typeof useSWR<PaginatedApiKeyList>> {
  return useSWR<PaginatedApiKeyList>(
    params ? ['cfg-grpc-api-keys', params] : 'cfg-grpc-api-keys',
    () => Fetchers.getGrpcApiKeysList(params, client)
  )
}


/**
 * Get API key details
 *
 * @method GET
 * @path /cfg/grpc/api-keys/{id}/
 */
export function useGrpcApiKeysRetrieve(id: number, client?: API): ReturnType<typeof useSWR<ApiKey>> {
  return useSWR<ApiKey>(
    ['cfg-grpc-api-key', id],
    () => Fetchers.getGrpcApiKeysRetrieve(id, client)
  )
}


/**
 * Get API keys statistics
 *
 * @method GET
 * @path /cfg/grpc/api-keys/stats/
 */
export function useGrpcApiKeysStatsRetrieve(client?: API): ReturnType<typeof useSWR<ApiKeyStats>> {
  return useSWR<ApiKeyStats>(
    'cfg-grpc-api-keys-stat',
    () => Fetchers.getGrpcApiKeysStatsRetrieve(client)
  )
}


