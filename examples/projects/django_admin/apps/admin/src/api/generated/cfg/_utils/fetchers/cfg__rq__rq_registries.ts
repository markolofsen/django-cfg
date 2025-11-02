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
import { getAPIInstance } from '../../api-instance'

/**
 * List deferred jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/deferred/
 */
export async function getRqJobsRegistriesDeferredList(  params?: { queue?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesDeferredList(params?.queue)
  return response
}


/**
 * List failed jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/failed/
 */
export async function getRqJobsRegistriesFailedList(  params?: { queue?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedList(params?.queue)
  return response
}


/**
 * Clear failed jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/clear/
 */
export async function createRqJobsRegistriesFailedClearCreate(  params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedClearCreate(params.queue)
  return JobActionResponseSchema.parse(response)
}


/**
 * Requeue all failed jobs
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/requeue-all/
 */
export async function createRqJobsRegistriesFailedRequeueAllCreate(  params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedRequeueAllCreate(params.queue)
  return JobActionResponseSchema.parse(response)
}


/**
 * List finished jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/finished/
 */
export async function getRqJobsRegistriesFinishedList(  params?: { queue?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFinishedList(params?.queue)
  return response
}


/**
 * Clear finished jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/finished/clear/
 */
export async function createRqJobsRegistriesFinishedClearCreate(  params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFinishedClearCreate(params.queue)
  return JobActionResponseSchema.parse(response)
}


/**
 * List started jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/started/
 */
export async function getRqJobsRegistriesStartedList(  params?: { queue?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesStartedList(params?.queue)
  return response
}


