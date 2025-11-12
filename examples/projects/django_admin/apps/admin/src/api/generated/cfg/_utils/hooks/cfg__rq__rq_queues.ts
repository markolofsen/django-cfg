/**
 * SWR Hooks for RQ Queues
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
import * as Fetchers from '../fetchers/cfg__rq__rq_queues'
import type { API } from '../../index'
import type { QueueDetail } from '../schemas/QueueDetail.schema'

/**
 * List all queues
 *
 * @method GET
 * @path /cfg/rq/queues/
 */
export function useRqQueuesList(params?: { name?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-queues', params] : 'cfg-rq-queues',
    () => Fetchers.getRqQueuesList(params, client)
  )
}


/**
 * Get queue details
 *
 * @method GET
 * @path /cfg/rq/queues/{id}/
 */
export function useRqQueuesRetrieve(id: string, client?: API): ReturnType<typeof useSWR<QueueDetail>> {
  return useSWR<QueueDetail>(
    ['cfg-rq-queue', id],
    () => Fetchers.getRqQueuesRetrieve(id, client)
  )
}


/**
 * Empty queue
 *
 * @method POST
 * @path /cfg/rq/queues/{id}/empty/
 */
export function useCreateRqQueuesEmptyCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<any> => {
    const result = await Fetchers.createRqQueuesEmptyCreate(id, client)
    // Revalidate related queries
    mutate('cfg-rq-queues-empty')
    return result
  }
}


/**
 * Get queue jobs
 *
 * @method GET
 * @path /cfg/rq/queues/{id}/jobs/
 */
export function useRqQueuesJobsRetrieve(id: string, params?: { limit?: number; offset?: number }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    ['cfg-rq-queues-job', id],
    () => Fetchers.getRqQueuesJobsRetrieve(id, params, client)
  )
}


