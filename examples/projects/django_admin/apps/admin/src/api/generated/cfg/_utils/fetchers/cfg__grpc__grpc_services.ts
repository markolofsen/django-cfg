/**
 * Typed fetchers for Grpc Services
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
import { PaginatedServiceSummaryListSchema, type PaginatedServiceSummaryList } from '../schemas/PaginatedServiceSummaryList.schema'
import { ServiceDetailSchema, type ServiceDetail } from '../schemas/ServiceDetail.schema'
import { ServiceMethodsSchema, type ServiceMethods } from '../schemas/ServiceMethods.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List all services
 *
 * @method GET
 * @path /cfg/grpc/services/
 */
export async function getGrpcServicesList(  params?: { hours?: number; page?: number; page_size?: number },  client?: any
): Promise<PaginatedServiceSummaryList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_services.list(params?.hours, params?.page, params?.page_size)
  return PaginatedServiceSummaryListSchema.parse(response)
}


/**
 * Get service details
 *
 * @method GET
 * @path /cfg/grpc/services/{id}/
 */
export async function getGrpcServicesRetrieve(  id: string, pk: string,  client?: any
): Promise<ServiceDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_services.retrieve(id, pk)
  return ServiceDetailSchema.parse(response)
}


/**
 * Get service methods
 *
 * @method GET
 * @path /cfg/grpc/services/{id}/methods/
 */
export async function getGrpcServicesMethodsRetrieve(  id: string, pk: string,  client?: any
): Promise<ServiceMethods> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_services.methodsRetrieve(id, pk)
  return ServiceMethodsSchema.parse(response)
}


