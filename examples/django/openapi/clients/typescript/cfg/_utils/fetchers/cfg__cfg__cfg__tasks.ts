/**
 * Typed fetchers for Cfg Tasks
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
import { APIResponseSchema, type APIResponse } from '../schemas/APIResponse.schema'
import { APIResponseRequestSchema, type APIResponseRequest } from '../schemas/APIResponseRequest.schema'
import { QueueActionSchema, type QueueAction } from '../schemas/QueueAction.schema'
import { QueueActionRequestSchema, type QueueActionRequest } from '../schemas/QueueActionRequest.schema'
import { QueueStatusSchema, type QueueStatus } from '../schemas/QueueStatus.schema'
import { TaskStatisticsSchema, type TaskStatistics } from '../schemas/TaskStatistics.schema'
import { WorkerActionSchema, type WorkerAction } from '../schemas/WorkerAction.schema'
import { WorkerActionRequestSchema, type WorkerActionRequest } from '../schemas/WorkerActionRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * createCfgTasksApiClear
 *
 * Clear all test data from Redis.
 *
 * @method POST
 * @path /cfg/tasks/api/clear/
 */
export async function createCfgTasksApiClear(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiClearCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * createCfgTasksApiClearQueues
 *
 * Clear all tasks from all Dramatiq queues.
 *
 * @method POST
 * @path /cfg/tasks/api/clear-queues/
 */
export async function createCfgTasksApiClearQueues(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiClearQueuesCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * createCfgTasksApiPurgeFailed
 *
 * Purge all failed tasks from queues.
 *
 * @method POST
 * @path /cfg/tasks/api/purge-failed/
 */
export async function createCfgTasksApiPurgeFailed(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiPurgeFailedCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * createCfgTasksApiQueuesManage
 *
 * Manage queue operations (clear, purge, etc.).
 *
 * @method POST
 * @path /cfg/tasks/api/queues/manage/
 */
export async function createCfgTasksApiQueuesManage(
  data: QueueActionRequest,
  client?: API
): Promise<QueueAction> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiQueuesManageCreate(data)
  return QueueActionSchema.parse(response)
}

/**
 * getCfgTasksApiQueuesStatusById
 *
 * Get current status of all queues.
 *
 * @method GET
 * @path /cfg/tasks/api/queues/status/
 */
export async function getCfgTasksApiQueuesStatusById(
  client?: API
): Promise<QueueStatus> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiQueuesStatusRetrieve()
  return QueueStatusSchema.parse(response)
}

/**
 * createCfgTasksApiSimulate
 *
 * Simulate test data for dashboard testing.
 *
 * @method POST
 * @path /cfg/tasks/api/simulate/
 */
export async function createCfgTasksApiSimulate(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiSimulateCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * getCfgTasksApiTasksListById
 *
 * Get paginated task list with filtering.
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/list/
 */
export async function getCfgTasksApiTasksListById(
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiTasksListRetrieve()
  return APIResponseSchema.parse(response)
}

/**
 * getCfgTasksApiTasksStatsById
 *
 * Get task execution statistics.
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/stats/
 */
export async function getCfgTasksApiTasksStatsById(
  client?: API
): Promise<TaskStatistics> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiTasksStatsRetrieve()
  return TaskStatisticsSchema.parse(response)
}

/**
 * getCfgTasksApiWorkersListById
 *
 * Get detailed list of workers.
 *
 * @method GET
 * @path /cfg/tasks/api/workers/list/
 */
export async function getCfgTasksApiWorkersListById(
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiWorkersListRetrieve()
  return APIResponseSchema.parse(response)
}

/**
 * createCfgTasksApiWorkersManage
 *
 * Manage worker operations.
 *
 * @method POST
 * @path /cfg/tasks/api/workers/manage/
 */
export async function createCfgTasksApiWorkersManage(
  data: WorkerActionRequest,
  client?: API
): Promise<WorkerAction> {
  const api = client || getAPIInstance()

  const response = await api.cfg__tasks.cfgTasksApiWorkersManageCreate(data)
  return WorkerActionSchema.parse(response)
}

