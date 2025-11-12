/**
 * SWR Hooks for Grpc Proto Files
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
import * as Fetchers from '../fetchers/cfg__grpc__grpc_proto_files'
import type { API } from '../../index'
import type { ProtoGenerateRequestRequest } from '../schemas/ProtoGenerateRequestRequest.schema'
import type { ProtoGenerateResponse } from '../schemas/ProtoGenerateResponse.schema'

/**
 * List all proto files
 *
 * @method GET
 * @path /cfg/grpc/proto-files/
 */
export function useGrpcProtoFilesList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-grpc-proto-files',
    () => Fetchers.getGrpcProtoFilesList(client)
  )
}


/**
 * Download proto file
 *
 * @method GET
 * @path /cfg/grpc/proto-files/{id}/
 */
export function useGrpcProtoFilesRetrieve(id: string, pk: string, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    ['cfg-grpc-proto-file', id],
    () => Fetchers.getGrpcProtoFilesRetrieve(id, pk, client)
  )
}


/**
 * Download all proto files
 *
 * @method GET
 * @path /cfg/grpc/proto-files/download-all/
 */
export function useGrpcProtoFilesDownloadAllRetrieve(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-grpc-proto-files-download-all',
    () => Fetchers.getGrpcProtoFilesDownloadAllRetrieve(client)
  )
}


/**
 * Generate proto files
 *
 * @method POST
 * @path /cfg/grpc/proto-files/generate/
 */
export function useCreateGrpcProtoFilesGenerateCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ProtoGenerateRequestRequest, client?: API): Promise<ProtoGenerateResponse> => {
    const result = await Fetchers.createGrpcProtoFilesGenerateCreate(data, client)
    // Revalidate related queries
    mutate('cfg-grpc-proto-files-generate')
    return result
  }
}


