/**
 * SWR Hooks for Grpc Configuration
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
import * as Fetchers from '../fetchers/cfg__grpc__grpc_configuration'
import type { API } from '../../index'
import type { GRPCConfig } from '../schemas/GRPCConfig.schema'
import type { GRPCServerInfo } from '../schemas/GRPCServerInfo.schema'

/**
 * Get gRPC configuration
 *
 * @method GET
 * @path /cfg/grpc/config/config/
 */
export function useGrpcConfigConfigRetrieve(client?: API): ReturnType<typeof useSWR<GRPCConfig>> {
  return useSWR<GRPCConfig>(
    'cfg-grpc-config-config',
    () => Fetchers.getGrpcConfigConfigRetrieve(client)
  )
}


/**
 * Get server information
 *
 * @method GET
 * @path /cfg/grpc/config/server-info/
 */
export function useGrpcConfigServerInfoRetrieve(client?: API): ReturnType<typeof useSWR<GRPCServerInfo>> {
  return useSWR<GRPCServerInfo>(
    'cfg-grpc-config-server-info',
    () => Fetchers.getGrpcConfigServerInfoRetrieve(client)
  )
}


