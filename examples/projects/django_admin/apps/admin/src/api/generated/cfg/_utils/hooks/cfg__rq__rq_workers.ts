/**
 * SWR Hooks for RQ Workers
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
import * as Fetchers from '../fetchers/cfg__rq__rq_workers'
import type { API } from '../../index'
import type { WorkerStats } from '../schemas/WorkerStats.schema'

/**
 * List all workers
 *
 * @method GET
 * @path /cfg/rq/workers/
 */
export function useRqWorkersList(params?: { queue?: string; state?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-workers', params] : 'cfg-rq-workers',
    () => Fetchers.getRqWorkersList(params, client)
  )
}


/**
 * Get worker statistics
 *
 * @method GET
 * @path /cfg/rq/workers/stats/
 */
export function useRqWorkersStatsRetrieve(client?: API): ReturnType<typeof useSWR<WorkerStats>> {
  return useSWR<WorkerStats>(
    'cfg-rq-workers-stat',
    () => Fetchers.getRqWorkersStatsRetrieve(client)
  )
}


