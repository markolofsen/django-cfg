/**
 * Typed fetchers for RQ Queues
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
import { QueueDetailSchema, type QueueDetail } from '../schemas/QueueDetail.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List all queues
 *
 * @method GET
 * @path /cfg/rq/queues/
 */
export async function getRqQueuesList(  params?: { name?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_queues.list(params?.name)
  return response
}


/**
 * Get queue details
 *
 * @method GET
 * @path /cfg/rq/queues/{id}/
 */
export async function getRqQueuesRetrieve(  id: string,  client?: any
): Promise<QueueDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_queues.retrieve(id)
  return QueueDetailSchema.parse(response)
}


/**
 * Empty queue
 *
 * @method POST
 * @path /cfg/rq/queues/{id}/empty/
 */
export async function createRqQueuesEmptyCreate(  id: string,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_queues.emptyCreate(id)
  return response
}


/**
 * Get queue jobs
 *
 * @method GET
 * @path /cfg/rq/queues/{id}/jobs/
 */
export async function getRqQueuesJobsRetrieve(  id: string, params?: { limit?: number; offset?: number },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_queues.jobsRetrieve(id, params?.limit, params?.offset)
  return response
}


