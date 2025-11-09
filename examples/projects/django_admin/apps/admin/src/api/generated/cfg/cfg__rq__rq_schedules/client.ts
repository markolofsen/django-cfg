import * as Models from "./models";


/**
 * API endpoints for RQ Schedules.
 */
export class CfgRqSchedules {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(page?: number, page_size?: number, queue?: string): Promise<Models.PaginatedScheduledJobList>;
  async list(params?: { page?: number; page_size?: number; queue?: string }): Promise<Models.PaginatedScheduledJobList>;

  /**
   * List scheduled jobs
   * 
   * Returns list of all scheduled jobs across all queues.
   */
  async list(...args: any[]): Promise<Models.PaginatedScheduledJobList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], queue: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/rq/schedules/", { params });
    return response;
  }

  /**
   * Create scheduled job
   * 
   * Schedule a job to run at specific time, interval, or cron schedule.
   */
  async create(data: Models.ScheduleCreateRequest): Promise<Models.ScheduleActionResponse> {
    const response = await this.client.request('POST', "/cfg/rq/schedules/", { body: data });
    return response;
  }

  async retrieve(id: string, pk: string, queue?: string): Promise<Models.ScheduledJob>;
  async retrieve(id: string, pk: string, params?: { queue?: string }): Promise<Models.ScheduledJob>;

  /**
   * Get scheduled job details
   * 
   * Returns detailed information about a specific scheduled job.
   */
  async retrieve(...args: any[]): Promise<Models.ScheduledJob> {
    const id = args[0];
    const pk = args[1];
    const isParamsObject = args.length === 3 && typeof args[2] === 'object' && args[2] !== null && !Array.isArray(args[2]);
    
    let params;
    if (isParamsObject) {
      params = args[2];
    } else {
      params = { queue: args[2] };
    }
    const response = await this.client.request('GET', `/cfg/rq/schedules/${id}/`, { params });
    return response;
  }

  async destroy(id: string, pk: string, queue?: string): Promise<Models.ScheduleActionResponse>;
  async destroy(id: string, pk: string, params?: { queue?: string }): Promise<Models.ScheduleActionResponse>;

  /**
   * Cancel scheduled job
   * 
   * Cancel a scheduled job by ID.
   */
  async destroy(...args: any[]): Promise<Models.ScheduleActionResponse> {
    const id = args[0];
    const pk = args[1];
    const isParamsObject = args.length === 3 && typeof args[2] === 'object' && args[2] !== null && !Array.isArray(args[2]);
    
    let params;
    if (isParamsObject) {
      params = args[2];
    } else {
      params = { queue: args[2] };
    }
    const response = await this.client.request('DELETE', `/cfg/rq/schedules/${id}/`, { params });
    return response;
  }

}