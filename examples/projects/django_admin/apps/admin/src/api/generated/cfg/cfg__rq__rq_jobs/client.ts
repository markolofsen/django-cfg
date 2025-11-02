import * as Models from "./models";


/**
 * API endpoints for RQ Jobs.
 */
export class CfgRqJobs {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(queue?: string, status?: string): Promise<any>;
  async list(params?: { queue?: string; status?: string }): Promise<any>;

  /**
   * List all jobs
   * 
   * Returns all jobs across all registries (queued, started, finished,
   * failed, deferred, scheduled).
   */
  async list(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0], status: args[1] };
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
  async cancelCreate(id: string): Promise<Models.JobActionResponse> {
    const response = await this.client.request('POST', `/cfg/rq/jobs/${id}/cancel/`);
    return response;
  }

  /**
   * Requeue job
   * 
   * Requeues a failed job.
   */
  async requeueCreate(id: string): Promise<Models.JobActionResponse> {
    const response = await this.client.request('POST', `/cfg/rq/jobs/${id}/requeue/`);
    return response;
  }

}