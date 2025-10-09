/**
 * SWR Hooks for Cfg Tasks
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
 * @path /cfg/tasks/api/queues/status/
 */
export function useCfgTasksApiQueuesStatusById() {
  return useSWR<QueueStatus>(
    'cfg-tasks-api-queues-statu',
    () => Fetchers.getCfgTasksApiQueuesStatusById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/list/
 */
export function useCfgTasksApiTasksListById() {
  return useSWR<APIResponse>(
    'cfg-tasks-api-task',
    () => Fetchers.getCfgTasksApiTasksListById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/stats/
 */
export function useCfgTasksApiTasksStatsById() {
  return useSWR<TaskStatistics>(
    'cfg-tasks-api-tasks-stat',
    () => Fetchers.getCfgTasksApiTasksStatsById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/tasks/api/workers/list/
 */
export function useCfgTasksApiWorkersListById() {
  return useSWR<APIResponse>(
    'cfg-tasks-api-worker',
    () => Fetchers.getCfgTasksApiWorkersListById()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /cfg/tasks/api/clear/
 */
export function useCreateCfgTasksApiClear() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createCfgTasksApiClear(data)

    // Revalidate related queries
    mutate('cfg-tasks-api-clear')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/tasks/api/clear-queues/
 */
export function useCreateCfgTasksApiClearQueues() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createCfgTasksApiClearQueues(data)

    // Revalidate related queries
    mutate('cfg-tasks-api-clear-queues')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/tasks/api/purge-failed/
 */
export function useCreateCfgTasksApiPurgeFailed() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createCfgTasksApiPurgeFailed(data)

    // Revalidate related queries
    mutate('cfg-tasks-api-purge-failed')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/tasks/api/queues/manage/
 */
export function useCreateCfgTasksApiQueuesManage() {
  const { mutate } = useSWRConfig()

  return async (data: QueueActionRequest): Promise<QueueAction> => {
    const result = await Fetchers.createCfgTasksApiQueuesManage(data)

    // Revalidate related queries
    mutate('cfg-tasks-api-queues-manage')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/tasks/api/simulate/
 */
export function useCreateCfgTasksApiSimulate() {
  const { mutate } = useSWRConfig()

  return async (data: APIResponseRequest): Promise<APIResponse> => {
    const result = await Fetchers.createCfgTasksApiSimulate(data)

    // Revalidate related queries
    mutate('cfg-tasks-api-simulate')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/tasks/api/workers/manage/
 */
export function useCreateCfgTasksApiWorkersManage() {
  const { mutate } = useSWRConfig()

  return async (data: WorkerActionRequest): Promise<WorkerAction> => {
    const result = await Fetchers.createCfgTasksApiWorkersManage(data)

    // Revalidate related queries
    mutate('cfg-tasks-api-workers-manage')

    return result
  }
}
