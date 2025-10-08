/**
 * SWR Hooks for Tasks
 *
 * Auto-generated React hooks for data fetching with SWR.
 *
 * Setup:
 * ```typescript
 * // Configure API once (in your app root)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 * ```
 *
 * Usage:
 * ```typescript
 * // Query hook
 * const { data, error, mutate } = useShopProducts({ page: 1 })
 *
 * // Mutation hook
 * const createProduct = useCreateShopProduct()
 * await createProduct({ name: 'Product', price: 99 })
 * ```
 */
import type { APIResponse } from '../schemas/APIResponse.schema'
import type { APIResponseRequest } from '../schemas/APIResponseRequest.schema'
import type { QueueAction } from '../schemas/QueueAction.schema'
import type { QueueActionRequest } from '../schemas/QueueActionRequest.schema'
import type { QueueStatus } from '../schemas/QueueStatus.schema'
import type { TaskStatistics } from '../schemas/TaskStatistics.schema'
import type { WorkerAction } from '../schemas/WorkerAction.schema'
import type { WorkerActionRequest } from '../schemas/WorkerActionRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 *
 * @method GET
 * @path /tasks/api/queues/status/
 */
export function useTasksApiQueuesStatusById() {
  return useSWR<QueueStatus>(
    'tasks-api-queues-statu',
    () => Fetchers.getTasksApiQueuesStatusById()
  )
}

/**
 *
 * @method GET
 * @path /tasks/api/tasks/list/
 */
export function useTasksApiTasksListById() {
  return useSWR<APIResponse>(
    'tasks-api-task',
    () => Fetchers.getTasksApiTasksListById()
  )
}

/**
 *
 * @method GET
 * @path /tasks/api/tasks/stats/
 */
export function useTasksApiTasksStatsById() {
  return useSWR<TaskStatistics>(
    'tasks-api-tasks-stat',
    () => Fetchers.getTasksApiTasksStatsById()
  )
}

/**
 *
 * @method GET
 * @path /tasks/api/workers/list/
 */
export function useTasksApiWorkersListById() {
  return useSWR<APIResponse>(
    'tasks-api-worker',
    () => Fetchers.getTasksApiWorkersListById()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /tasks/api/clear/
 */
export function useCreateTasksApiClear() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiClear(data)

    // Revalidate related queries
    mutate('tasks-api-clear')

    return result
  }
}

/**
 *
 * @method POST
 * @path /tasks/api/clear-queues/
 */
export function useCreateTasksApiClearQueues() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiClearQueues(data)

    // Revalidate related queries
    mutate('tasks-api-clear-queues')

    return result
  }
}

/**
 *
 * @method POST
 * @path /tasks/api/purge-failed/
 */
export function useCreateTasksApiPurgeFailed() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiPurgeFailed(data)

    // Revalidate related queries
    mutate('tasks-api-purge-failed')

    return result
  }
}

/**
 *
 * @method POST
 * @path /tasks/api/queues/manage/
 */
export function useCreateTasksApiQueuesManage() {
  const { mutate } = useSWRConfig()

  return async (data: QueueActionRequest): Promise<QueueAction> => {
    const result = await Fetchers.createTasksApiQueuesManage(data)

    // Revalidate related queries
    mutate('tasks-api-queues-manage')

    return result
  }
}

/**
 *
 * @method POST
 * @path /tasks/api/simulate/
 */
export function useCreateTasksApiSimulate() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createTasksApiSimulate(data)

    // Revalidate related queries
    mutate('tasks-api-simulate')

    return result
  }
}

/**
 *
 * @method POST
 * @path /tasks/api/workers/manage/
 */
export function useCreateTasksApiWorkersManage() {
  const { mutate } = useSWRConfig()

  return async (data: WorkerActionRequest): Promise<WorkerAction> => {
    const result = await Fetchers.createTasksApiWorkersManage(data)

    // Revalidate related queries
    mutate('tasks-api-workers-manage')

    return result
  }
}
