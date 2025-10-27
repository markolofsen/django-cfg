import { BaseAPIClient } from '../base.mjs';

/**
 * Tasks API Client
 * Auto-generated from OpenAPI schema
 * @module tasks
 * @extends BaseAPIClient
 */
export class TasksAPI extends BaseAPIClient {
    /**
     * Initialize tasks API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * tasksApiClearCreate     * Clear all test data from Redis.     * @param {APIResponseRequest} data - Request body     * @returns {Promise<APIResponse>} Response data
     */
    async tasksApiClearCreate(data) {
        const path = `/cfg/tasks/api/clear/`;        return this.post(path, data);    }
    /**
     * tasksApiClearQueuesCreate     * Clear all tasks from all Dramatiq queues.     * @param {APIResponseRequest} data - Request body     * @returns {Promise<APIResponse>} Response data
     */
    async tasksApiClearQueuesCreate(data) {
        const path = `/cfg/tasks/api/clear-queues/`;        return this.post(path, data);    }
    /**
     * tasksApiPurgeFailedCreate     * Purge all failed tasks from queues.     * @param {APIResponseRequest} data - Request body     * @returns {Promise<APIResponse>} Response data
     */
    async tasksApiPurgeFailedCreate(data) {
        const path = `/cfg/tasks/api/purge-failed/`;        return this.post(path, data);    }
    /**
     * tasksApiQueuesManageCreate     * Manage queue operations (clear, purge, etc.).     * @param {QueueActionRequest} data - Request body     * @returns {Promise<QueueAction>} Response data
     */
    async tasksApiQueuesManageCreate(data) {
        const path = `/cfg/tasks/api/queues/manage/`;        return this.post(path, data);    }
    /**
     * tasksApiQueuesStatusRetrieve     * Get current status of all queues.     * @returns {Promise<QueueStatus>} Response data
     */
    async tasksApiQueuesStatusRetrieve() {
        const path = `/cfg/tasks/api/queues/status/`;        return this.get(path);    }
    /**
     * tasksApiSimulateCreate     * Simulate test data for dashboard testing.     * @param {APIResponseRequest} data - Request body     * @returns {Promise<APIResponse>} Response data
     */
    async tasksApiSimulateCreate(data) {
        const path = `/cfg/tasks/api/simulate/`;        return this.post(path, data);    }
    /**
     * tasksApiTasksListRetrieve     * Get paginated task list with filtering.     * @returns {Promise<APIResponse>} Response data
     */
    async tasksApiTasksListRetrieve() {
        const path = `/cfg/tasks/api/tasks/list/`;        return this.get(path);    }
    /**
     * tasksApiTasksStatsRetrieve     * Get task execution statistics.     * @returns {Promise<TaskStatistics>} Response data
     */
    async tasksApiTasksStatsRetrieve() {
        const path = `/cfg/tasks/api/tasks/stats/`;        return this.get(path);    }
    /**
     * tasksApiWorkersListRetrieve     * Get detailed list of workers.     * @returns {Promise<APIResponse>} Response data
     */
    async tasksApiWorkersListRetrieve() {
        const path = `/cfg/tasks/api/workers/list/`;        return this.get(path);    }
    /**
     * tasksApiWorkersManageCreate     * Manage worker operations.     * @param {WorkerActionRequest} data - Request body     * @returns {Promise<WorkerAction>} Response data
     */
    async tasksApiWorkersManageCreate(data) {
        const path = `/cfg/tasks/api/workers/manage/`;        return this.post(path, data);    }
}

// Default instance for convenience
export const tasksAPI = new TasksAPI();

// Default export
export default TasksAPI;