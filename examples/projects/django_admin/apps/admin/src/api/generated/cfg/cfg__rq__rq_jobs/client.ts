import * as Models from "./models";


/**
 * API endpoints for RQ Jobs.
 */
export class CfgRqJobs {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(page?: number, page_size?: number, queue?: string, status?: string): Promise<Models.PaginatedJobListList>;
  async list(params?: { page?: number; page_size?: number; queue?: string; status?: string }): Promise<Models.PaginatedJobListList>;

  /**
   * List all jobs
   * 
   * Returns all jobs across all registries (queued, started, finished,
   * failed, deferred, scheduled).
   */
  async list(...args: any[]): Promise<Models.PaginatedJobListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], queue: args[2], status: args[3] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/", { params });
    return response;
  }

  /**
   * Get job details
   * 
   * Returns detailed information about a specific job.
   */
  async retrieve(id: string): Promise<Models.JobDetail> {
    const response = await this.client.request('GET', `/cfg/rq/jobs/${id}/`);
    return response;
  }

  /**
   * Delete job
   * 
   * Deletes a job from the queue.
   */
  async destroy(id: string): Promise<Models.JobActionResponse> {
    const response = await this.client.request('DELETE', `/cfg/rq/jobs/${id}/`);
    return response;
  }

  /**
   * Cancel job
   * 
   * Cancels a job (if it's queued or started).
   */
  async cancelCreate(id: string, data: Models.JobListRequest): Promise<Models.JobActionResponse> {
    const response = await this.client.request('POST', `/cfg/rq/jobs/${id}/cancel/`, { body: data });
    return response;
  }

  /**
   * Requeue job
   * 
   * Requeues a failed job.
   */
  async requeueCreate(id: string, data: Models.JobListRequest): Promise<Models.JobActionResponse> {
    const response = await this.client.request('POST', `/cfg/rq/jobs/${id}/requeue/`, { body: data });
    return response;
  }

}