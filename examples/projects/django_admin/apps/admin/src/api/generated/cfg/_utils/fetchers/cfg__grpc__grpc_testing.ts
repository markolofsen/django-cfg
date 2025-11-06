/**
 * Typed fetchers for Grpc Testing
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
import { GRPCCallRequestRequestSchema, type GRPCCallRequestRequest } from '../schemas/GRPCCallRequestRequest.schema'
import { GRPCCallResponseSchema, type GRPCCallResponse } from '../schemas/GRPCCallResponse.schema'
import { GRPCExamplesListSchema, type GRPCExamplesList } from '../schemas/GRPCExamplesList.schema'
import { GRPCTestLogSchema, type GRPCTestLog } from '../schemas/GRPCTestLog.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Call gRPC method
 *
 * @method POST
 * @path /cfg/grpc/test/call/
 */
export async function createGrpcTestCallCreate(  data: GRPCCallRequestRequest,  client?: any
): Promise<GRPCCallResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_testing.grpcTestCallCreate(data)
  return GRPCCallResponseSchema.parse(response)
}


/**
 * Get example payloads
 *
 * @method GET
 * @path /cfg/grpc/test/examples/
 */
export async function getGrpcTestExamplesRetrieve(  params?: { method?: string; service?: string },  client?: any
): Promise<GRPCExamplesList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_testing.grpcTestExamplesRetrieve(params?.method, params?.service)
  return GRPCExamplesListSchema.parse(response)
}


/**
 * Get test logs
 *
 * @method GET
 * @path /cfg/grpc/test/logs/
 */
export async function getGrpcTestLogsRetrieve(  params?: { method?: string; service?: string; status?: string },  client?: any
): Promise<GRPCTestLog> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_testing.grpcTestLogsRetrieve(params?.method, params?.service, params?.status)
  return GRPCTestLogSchema.parse(response)
}


