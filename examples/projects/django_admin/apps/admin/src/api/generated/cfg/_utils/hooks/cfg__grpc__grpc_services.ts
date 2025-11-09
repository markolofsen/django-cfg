/**
 * SWR Hooks for Grpc Services
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
import * as Fetchers from '../fetchers/cfg__grpc__grpc_services'
import type { API } from '../../index'
import type { PaginatedServiceSummaryList } from '../schemas/PaginatedServiceSummaryList.schema'
import type { ServiceDetail } from '../schemas/ServiceDetail.schema'
import type { ServiceMethods } from '../schemas/ServiceMethods.schema'

/**
 * List all services
 *
 * @method GET
 * @path /cfg/grpc/services/
 */
export function useGrpcServicesList(params?: { hours?: number; page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedServiceSummaryList>> {
  return useSWR<PaginatedServiceSummaryList>(
    params ? ['cfg-grpc-services', params] : 'cfg-grpc-services',
    () => Fetchers.getGrpcServicesList(params, client)
  )
}


/**
 * Get service details
 *
 * @method GET
 * @path /cfg/grpc/services/{id}/
 */
export function useGrpcServicesRetrieve(id: string, pk: string, client?: API): ReturnType<typeof useSWR<ServiceDetail>> {
  return useSWR<ServiceDetail>(
    ['cfg-grpc-service', id],
    () => Fetchers.getGrpcServicesRetrieve(id, pk, client)
  )
}


/**
 * Get service methods
 *
 * @method GET
 * @path /cfg/grpc/services/{id}/methods/
 */
export function useGrpcServicesMethodsRetrieve(id: string, pk: string, client?: API): ReturnType<typeof useSWR<ServiceMethods>> {
  return useSWR<ServiceMethods>(
    ['cfg-grpc-services-method', id],
    () => Fetchers.getGrpcServicesMethodsRetrieve(id, pk, client)
  )
}


