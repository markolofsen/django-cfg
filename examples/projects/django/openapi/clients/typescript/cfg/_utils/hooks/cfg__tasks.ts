/**
 * SWR Hooks for Tasks
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
import * as Fetchers from '../fetchers/cfg__tasks'
import type { API } from '../../index'
import type { APIResponse } from '../schemas/APIResponse.schema'
import type { APIResponseRequest } from '../schemas/APIResponseRequest.schema'
import type { QueueAction } from '../schemas/QueueAction.schema'
import type { QueueActionRequest } from '../schemas/QueueActionRequest.schema'
import type { QueueStatus } from '../schemas/QueueStatus.schema'
import type { TaskStatistics } from '../schemas/TaskStatistics.schema'
import type { WorkerAction } from '../schemas/WorkerAction.schema'
import type { WorkerActionRequest } from '../schemas/WorkerActionRequest.schema'

/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/clear/
 */
export function useCreateTasksApiClearCreate() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest, client?: API): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiClearCreate(data, client)
    // Revalidate related queries
    mutate('cfg-tasks-api-clear')
    return result
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/clear-queues/
 */
export function useCreateTasksApiClearQueuesCreate() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest, client?: API): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiClearQueuesCreate(data, client)
    // Revalidate related queries
    mutate('cfg-tasks-api-clear-queues')
    return result
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/purge-failed/
 */
export function useCreateTasksApiPurgeFailedCreate() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest, client?: API): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiPurgeFailedCreate(data, client)
    // Revalidate related queries
    mutate('cfg-tasks-api-purge-failed')
    return result
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/queues/manage/
 */
export function useCreateTasksApiQueuesManageCreate() {
  const { mutate } = useSWRConfig()

  return async (data: QueueActionRequest, client?: API): Promise<QueueAction> => {
    const result = await Fetchers.createTasksApiQueuesManageCreate(data, client)
    // Revalidate related queries
    mutate('cfg-tasks-api-queues-manage')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/queues/status/
 */
export function useTasksApiQueuesStatusRetrieve(client?: API): ReturnType<typeof useSWR<QueueStatus>> {
  return useSWR<QueueStatus>(
    'cfg-tasks-api-queues-statu',
    () => Fetchers.getTasksApiQueuesStatusRetrieve(client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/simulate/
 */
export function useCreateTasksApiSimulateCreate() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest, client?: API): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiSimulateCreate(data, client)
    // Revalidate related queries
    mutate('cfg-tasks-api-simulate')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/list/
 */
export function useTasksApiTasksListRetrieve(client?: API): ReturnType<typeof useSWR<APIResponse>> {
  return useSWR<APIResponse>(
    'cfg-tasks-api-task',
    () => Fetchers.getTasksApiTasksListRetrieve(client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/stats/
 */
export function useTasksApiTasksStatsRetrieve(client?: API): ReturnType<typeof useSWR<TaskStatistics>> {
  return useSWR<TaskStatistics>(
    'cfg-tasks-api-tasks-stat',
    () => Fetchers.getTasksApiTasksStatsRetrieve(client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/workers/list/
 */
export function useTasksApiWorkersListRetrieve(client?: API): ReturnType<typeof useSWR<APIResponse>> {
  return useSWR<APIResponse>(
    'cfg-tasks-api-worker',
    () => Fetchers.getTasksApiWorkersListRetrieve(client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/workers/manage/
 */
export function useCreateTasksApiWorkersManageCreate() {
  const { mutate } = useSWRConfig()

  return async (data: WorkerActionRequest, client?: API): Promise<WorkerAction> => {
    const result = await Fetchers.createTasksApiWorkersManageCreate(data, client)
    // Revalidate related queries
    mutate('cfg-tasks-api-workers-manage')
    return result
  }
}


