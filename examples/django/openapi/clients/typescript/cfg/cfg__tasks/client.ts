import * as Models from "./models";


/**
 * API endpoints for Tasks.
 */
export class CfgTasksAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * Clear all test data from Redis.
 */
async apiClearCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
  const response = await this.client.request<Models.APIResponse>('POST', "/tasks/api/clear/", { body: data });
  return response;
}

  /**
 * Clear all tasks from all Dramatiq queues.
 */
async apiClearQueuesCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
  const response = await this.client.request<Models.APIResponse>('POST', "/tasks/api/clear-queues/", { body: data });
  return response;
}

  /**
 * Purge all failed tasks from queues.
 */
async apiPurgeFailedCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
  const response = await this.client.request<Models.APIResponse>('POST', "/tasks/api/purge-failed/", { body: data });
  return response;
}

  /**
 * Manage queue operations (clear, purge, etc.).
 */
async apiQueuesManageCreate(data: Models.QueueActionRequest): Promise<Models.QueueAction> {
  const response = await this.client.request<Models.QueueAction>('POST', "/tasks/api/queues/manage/", { body: data });
  return response;
}

  /**
 * Get current status of all queues.
 */
async apiQueuesStatusRetrieve(): Promise<Models.QueueStatus> {
  const response = await this.client.request<Models.QueueStatus>('GET', "/tasks/api/queues/status/");
  return response;
}

  /**
 * Simulate test data for dashboard testing.
 */
async apiSimulateCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
  const response = await this.client.request<Models.APIResponse>('POST', "/tasks/api/simulate/", { body: data });
  return response;
}

  /**
 * Get paginated task list with filtering.
 */
async apiTasksListRetrieve(): Promise<Models.APIResponse> {
  const response = await this.client.request<Models.APIResponse>('GET', "/tasks/api/tasks/list/");
  return response;
}

  /**
 * Get task execution statistics.
 */
async apiTasksStatsRetrieve(): Promise<Models.TaskStatistics> {
  const response = await this.client.request<Models.TaskStatistics>('GET', "/tasks/api/tasks/stats/");
  return response;
}

  /**
 * Get detailed list of workers.
 */
async apiWorkersListRetrieve(): Promise<Models.APIResponse> {
  const response = await this.client.request<Models.APIResponse>('GET', "/tasks/api/workers/list/");
  return response;
}

  /**
 * Manage worker operations.
 */
async apiWorkersManageCreate(data: Models.WorkerActionRequest): Promise<Models.WorkerAction> {
  const response = await this.client.request<Models.WorkerAction>('POST', "/tasks/api/workers/manage/", { body: data });
  return response;
}

}