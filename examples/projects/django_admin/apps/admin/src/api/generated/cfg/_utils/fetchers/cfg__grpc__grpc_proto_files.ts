/**
 * Typed fetchers for Grpc Proto Files
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
import { ProtoGenerateRequestRequestSchema, type ProtoGenerateRequestRequest } from '../schemas/ProtoGenerateRequestRequest.schema'
import { ProtoGenerateResponseSchema, type ProtoGenerateResponse } from '../schemas/ProtoGenerateResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List all proto files
 *
 * @method GET
 * @path /cfg/grpc/proto-files/
 */
export async function getGrpcProtoFilesList(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_proto_files.list()
  return response
}


/**
 * Download proto file
 *
 * @method GET
 * @path /cfg/grpc/proto-files/{id}/
 */
export async function getGrpcProtoFilesRetrieve(  id: string, pk: string,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_proto_files.retrieve(id, pk)
  return response
}


/**
 * Download all proto files
 *
 * @method GET
 * @path /cfg/grpc/proto-files/download-all/
 */
export async function getGrpcProtoFilesDownloadAllRetrieve(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_proto_files.downloadAllRetrieve()
  return response
}


/**
 * Generate proto files
 *
 * @method POST
 * @path /cfg/grpc/proto-files/generate/
 */
export async function createGrpcProtoFilesGenerateCreate(  data: ProtoGenerateRequestRequest,  client?: any
): Promise<ProtoGenerateResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_proto_files.generateCreate(data)
  return ProtoGenerateResponseSchema.parse(response)
}


