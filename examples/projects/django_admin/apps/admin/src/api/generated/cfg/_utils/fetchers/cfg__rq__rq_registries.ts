/**
 * Typed fetchers for RQ Registries
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
import { JobActionResponseSchema, type JobActionResponse } from '../schemas/JobActionResponse.schema'
import { JobListRequestSchema, type JobListRequest } from '../schemas/JobListRequest.schema'
import { PaginatedJobListListSchema, type PaginatedJobListList } from '../schemas/PaginatedJobListList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List deferred jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/deferred/
 */
export async function getRqJobsRegistriesDeferredList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesDeferredList(params?.page, params?.page_size, params?.queue)
  return PaginatedJobListListSchema.parse(response)
}


/**
 * List failed jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/failed/
 */
export async function getRqJobsRegistriesFailedList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedList(params?.page, params?.page_size, params?.queue)
  return PaginatedJobListListSchema.parse(response)
}


/**
 * Clear failed jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/clear/
 */
export async function createRqJobsRegistriesFailedClearCreate(  data: JobListRequest, params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedClearCreate(data, params.queue)
  return JobActionResponseSchema.parse(response)
}


/**
 * Requeue all failed jobs
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/requeue-all/
 */
export async function createRqJobsRegistriesFailedRequeueAllCreate(  data: JobListRequest, params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedRequeueAllCreate(data, params.queue)
  return JobActionResponseSchema.parse(response)
}


/**
 * List finished jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/finished/
 */
export async function getRqJobsRegistriesFinishedList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFinishedList(params?.page, params?.page_size, params?.queue)
  return PaginatedJobListListSchema.parse(response)
}


/**
 * Clear finished jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/finished/clear/
 */
export async function createRqJobsRegistriesFinishedClearCreate(  data: JobListRequest, params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFinishedClearCreate(data, params.queue)
  return JobActionResponseSchema.parse(response)
}


/**
 * List started jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/started/
 */
export async function getRqJobsRegistriesStartedList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesStartedList(params?.page, params?.page_size, params?.queue)
  return PaginatedJobListListSchema.parse(response)
}


