import * as Models from "./models";


/**
 * API endpoints for RQ Registries.
 */
export class CfgRqRegistries {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async rqJobsRegistriesDeferredList(page?: number, page_size?: number, queue?: string): Promise<Models.PaginatedJobListList>;
  async rqJobsRegistriesDeferredList(params?: { page?: number; page_size?: number; queue?: string }): Promise<Models.PaginatedJobListList>;

  /**
   * List deferred jobs
   * 
   * Returns list of all deferred jobs from deferred job registry.
   */
  async rqJobsRegistriesDeferredList(...args: any[]): Promise<Models.PaginatedJobListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], queue: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/deferred/", { params });
    return response;
  }

  async rqJobsRegistriesFailedList(page?: number, page_size?: number, queue?: string): Promise<Models.PaginatedJobListList>;
  async rqJobsRegistriesFailedList(params?: { page?: number; page_size?: number; queue?: string }): Promise<Models.PaginatedJobListList>;

  /**
   * List failed jobs
   * 
   * Returns list of all failed jobs from failed job registry.
   */
  async rqJobsRegistriesFailedList(...args: any[]): Promise<Models.PaginatedJobListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], queue: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/failed/", { params });
    return response;
  }

  async rqJobsRegistriesFailedClearCreate(data: Models.JobListRequest, queue: string): Promise<Models.JobActionResponse>;
  async rqJobsRegistriesFailedClearCreate(data: Models.JobListRequest, params: { queue: string }): Promise<Models.JobActionResponse>;

  /**
   * Clear failed jobs registry
   * 
   * Removes all jobs from the failed job registry.
   */
  async rqJobsRegistriesFailedClearCreate(...args: any[]): Promise<Models.JobActionResponse> {
    const data = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { queue: args[1] };
    }
    const response = await this.client.request('POST', "/cfg/rq/jobs/registries/failed/clear/", { params, body: data });
    return response;
  }

  async rqJobsRegistriesFailedRequeueAllCreate(data: Models.JobListRequest, queue: string): Promise<Models.JobActionResponse>;
  async rqJobsRegistriesFailedRequeueAllCreate(data: Models.JobListRequest, params: { queue: string }): Promise<Models.JobActionResponse>;

  /**
   * Requeue all failed jobs
   * 
   * Requeues all failed jobs in the failed job registry.
   */
  async rqJobsRegistriesFailedRequeueAllCreate(...args: any[]): Promise<Models.JobActionResponse> {
    const data = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { queue: args[1] };
    }
    const response = await this.client.request('POST', "/cfg/rq/jobs/registries/failed/requeue-all/", { params, body: data });
    return response;
  }

  async rqJobsRegistriesFinishedList(page?: number, page_size?: number, queue?: string): Promise<Models.PaginatedJobListList>;
  async rqJobsRegistriesFinishedList(params?: { page?: number; page_size?: number; queue?: string }): Promise<Models.PaginatedJobListList>;

  /**
   * List finished jobs
   * 
   * Returns list of all finished jobs from finished job registry.
   */
  async rqJobsRegistriesFinishedList(...args: any[]): Promise<Models.PaginatedJobListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], queue: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/finished/", { params });
    return response;
  }

  async rqJobsRegistriesFinishedClearCreate(data: Models.JobListRequest, queue: string): Promise<Models.JobActionResponse>;
  async rqJobsRegistriesFinishedClearCreate(data: Models.JobListRequest, params: { queue: string }): Promise<Models.JobActionResponse>;

  /**
   * Clear finished jobs registry
   * 
   * Removes all jobs from the finished job registry.
   */
  async rqJobsRegistriesFinishedClearCreate(...args: any[]): Promise<Models.JobActionResponse> {
    const data = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { queue: args[1] };
    }
    const response = await this.client.request('POST', "/cfg/rq/jobs/registries/finished/clear/", { params, body: data });
    return response;
  }

  async rqJobsRegistriesStartedList(page?: number, page_size?: number, queue?: string): Promise<Models.PaginatedJobListList>;
  async rqJobsRegistriesStartedList(params?: { page?: number; page_size?: number; queue?: string }): Promise<Models.PaginatedJobListList>;

  /**
   * List started jobs
   * 
   * Returns list of all currently running jobs from started job registry.
   */
  async rqJobsRegistriesStartedList(...args: any[]): Promise<Models.PaginatedJobListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], queue: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/started/", { params });
    return response;
  }

}