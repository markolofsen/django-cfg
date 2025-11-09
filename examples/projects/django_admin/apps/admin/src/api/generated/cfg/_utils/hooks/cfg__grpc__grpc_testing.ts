/**
 * SWR Hooks for Grpc Testing
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
import * as Fetchers from '../fetchers/cfg__grpc__grpc_testing'
import type { API } from '../../index'
import type { GRPCCallRequestRequest } from '../schemas/GRPCCallRequestRequest.schema'
import type { GRPCCallResponse } from '../schemas/GRPCCallResponse.schema'
import type { GRPCExamplesList } from '../schemas/GRPCExamplesList.schema'
import type { GRPCTestLog } from '../schemas/GRPCTestLog.schema'

/**
 * Call gRPC method
 *
 * @method POST
 * @path /cfg/grpc/test/call/
 */
export function useCreateGrpcTestCallCreate() {
  const { mutate } = useSWRConfig()

  return async (data: GRPCCallRequestRequest, client?: API): Promise<GRPCCallResponse> => {
    const result = await Fetchers.createGrpcTestCallCreate(data, client)
    // Revalidate related queries
    mutate('cfg-grpc-test-call')
    return result
  }
}


/**
 * Get example payloads
 *
 * @method GET
 * @path /cfg/grpc/test/examples/
 */
export function useGrpcTestExamplesRetrieve(params?: { method?: string; service?: string }, client?: API): ReturnType<typeof useSWR<GRPCExamplesList>> {
  return useSWR<GRPCExamplesList>(
    params ? ['cfg-grpc-test-example', params] : 'cfg-grpc-test-example',
    () => Fetchers.getGrpcTestExamplesRetrieve(params, client)
  )
}


/**
 * Get test logs
 *
 * @method GET
 * @path /cfg/grpc/test/logs/
 */
export function useGrpcTestLogsRetrieve(params?: { method?: string; service?: string; status?: string }, client?: API): ReturnType<typeof useSWR<GRPCTestLog>> {
  return useSWR<GRPCTestLog>(
    params ? ['cfg-grpc-test-log', params] : 'cfg-grpc-test-log',
    () => Fetchers.getGrpcTestLogsRetrieve(params, client)
  )
}


