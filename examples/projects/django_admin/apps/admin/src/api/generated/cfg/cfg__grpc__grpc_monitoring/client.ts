import * as Models from "./models";


/**
 * API endpoints for Grpc Monitoring.
 */
export class CfgGrpcMonitoring {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get gRPC health status
   * 
   * Returns the current health status of the gRPC server.
   */
  async grpcMonitorHealthRetrieve(): Promise<Models.GRPCHealthCheck> {
    const response = await this.client.request('GET', "/cfg/grpc/monitor/health/");
    return response;
  }

  async grpcMonitorMethodsRetrieve(hours?: number, service?: string): Promise<Models.MethodList[]>;
  async grpcMonitorMethodsRetrieve(params?: { hours?: number; service?: string }): Promise<Models.MethodList[]>;

  /**
   * Get method statistics
   * 
   * Returns statistics grouped by method.
   */
  async grpcMonitorMethodsRetrieve(...args: any[]): Promise<Models.MethodList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0], service: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/monitor/methods/", { params });
    return response;
  }

  async grpcMonitorOverviewRetrieve(hours?: number): Promise<Models.GRPCOverviewStats>;
  async grpcMonitorOverviewRetrieve(params?: { hours?: number }): Promise<Models.GRPCOverviewStats>;

  /**
   * Get overview statistics
   * 
   * Returns overview statistics for gRPC requests.
   */
  async grpcMonitorOverviewRetrieve(...args: any[]): Promise<Models.GRPCOverviewStats> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/monitor/overview/", { params });
    return response;
  }

  async grpcMonitorRequestsList(method?: string, page?: number, page_size?: number, service?: string, status?: string): Promise<Models.PaginatedRecentRequestList>;
  async grpcMonitorRequestsList(params?: { method?: string; page?: number; page_size?: number; service?: string; status?: string }): Promise<Models.PaginatedRecentRequestList>;

  /**
   * Get recent requests
   * 
   * Returns a list of recent gRPC requests with their details. Uses standard
   * DRF pagination.
   */
  async grpcMonitorRequestsList(...args: any[]): Promise<Models.PaginatedRecentRequestList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { method: args[0], page: args[1], page_size: args[2], service: args[3], status: args[4] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/monitor/requests/", { params });
    return response;
  }

  async grpcMonitorTimelineRetrieve(hours?: number, interval?: string): Promise<any>;
  async grpcMonitorTimelineRetrieve(params?: { hours?: number; interval?: string }): Promise<any>;

  /**
   * Get request timeline
   * 
   * Returns hourly or daily breakdown of request counts for charts.
   */
  async grpcMonitorTimelineRetrieve(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0], interval: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/monitor/timeline/", { params });
    return response;
  }

}