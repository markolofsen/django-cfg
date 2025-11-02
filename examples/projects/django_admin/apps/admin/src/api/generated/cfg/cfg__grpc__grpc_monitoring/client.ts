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
  async grpcMonitorHealthRetrieve(): Promise<Models.HealthCheck> {
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
    return (response as any).results || [];
  }

  async grpcMonitorOverviewRetrieve(hours?: number): Promise<Models.OverviewStats>;
  async grpcMonitorOverviewRetrieve(params?: { hours?: number }): Promise<Models.OverviewStats>;

  /**
   * Get overview statistics
   * 
   * Returns overview statistics for gRPC requests.
   */
  async grpcMonitorOverviewRetrieve(...args: any[]): Promise<Models.OverviewStats> {
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

  async grpcMonitorRequestsRetrieve(count?: number, method?: string, offset?: number, service?: string, status?: string): Promise<Models.RecentRequests>;
  async grpcMonitorRequestsRetrieve(params?: { count?: number; method?: string; offset?: number; service?: string; status?: string }): Promise<Models.RecentRequests>;

  /**
   * Get recent requests
   * 
   * Returns a list of recent gRPC requests with their details.
   */
  async grpcMonitorRequestsRetrieve(...args: any[]): Promise<Models.RecentRequests> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { count: args[0], method: args[1], offset: args[2], service: args[3], status: args[4] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/monitor/requests/", { params });
    return response;
  }

  async grpcMonitorServicesRetrieve(hours?: number): Promise<Models.ServiceList[]>;
  async grpcMonitorServicesRetrieve(params?: { hours?: number }): Promise<Models.ServiceList[]>;

  /**
   * Get service statistics
   * 
   * Returns statistics grouped by service.
   */
  async grpcMonitorServicesRetrieve(...args: any[]): Promise<Models.ServiceList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/monitor/services/", { params });
    return (response as any).results || [];
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