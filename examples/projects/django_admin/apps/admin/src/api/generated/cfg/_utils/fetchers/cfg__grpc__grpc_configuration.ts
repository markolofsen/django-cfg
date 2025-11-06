/**
 * Typed fetchers for Grpc Configuration
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
import { GRPCConfigSchema, type GRPCConfig } from '../schemas/GRPCConfig.schema'
import { GRPCServerInfoSchema, type GRPCServerInfo } from '../schemas/GRPCServerInfo.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get gRPC configuration
 *
 * @method GET
 * @path /cfg/grpc/config/config/
 */
export async function getGrpcConfigConfigRetrieve(  client?: any
): Promise<GRPCConfig> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_configuration.grpcConfigConfigRetrieve()
  return GRPCConfigSchema.parse(response)
}


/**
 * Get server information
 *
 * @method GET
 * @path /cfg/grpc/config/server-info/
 */
export async function getGrpcConfigServerInfoRetrieve(  client?: any
): Promise<GRPCServerInfo> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_configuration.grpcConfigServerInfoRetrieve()
  return GRPCServerInfoSchema.parse(response)
}


