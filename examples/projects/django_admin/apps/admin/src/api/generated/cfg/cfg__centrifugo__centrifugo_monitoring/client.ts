import * as Models from "./models";


/**
 * API endpoints for Centrifugo Monitoring.
 */
export class CfgCentrifugoMonitoring {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async centrifugoMonitorChannelsRetrieve(hours?: number): Promise<Models.ChannelList[]>;
  async centrifugoMonitorChannelsRetrieve(params?: { hours?: number }): Promise<Models.ChannelList[]>;

  /**
   * Get channel statistics
   * 
   * Returns statistics grouped by channel.
   */
  async centrifugoMonitorChannelsRetrieve(...args: any[]): Promise<Models.ChannelList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/channels/", { params });
    return (response as any).results || response;
  }

  /**
   * Get Centrifugo health status
   * 
   * Returns the current health status of the Centrifugo client.
   */
  async centrifugoMonitorHealthRetrieve(): Promise<Models.HealthCheck> {
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/health/");
    return response;
  }

  async centrifugoMonitorOverviewRetrieve(hours?: number): Promise<Models.CentrifugoOverviewStats>;
  async centrifugoMonitorOverviewRetrieve(params?: { hours?: number }): Promise<Models.CentrifugoOverviewStats>;

  /**
   * Get overview statistics
   * 
   * Returns overview statistics for Centrifugo publishes.
   */
  async centrifugoMonitorOverviewRetrieve(...args: any[]): Promise<Models.CentrifugoOverviewStats> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/overview/", { params });
    return response;
  }

  async centrifugoMonitorPublishesList(channel?: string, page?: number, page_size?: number, status?: string): Promise<Models.PaginatedPublishList>;
  async centrifugoMonitorPublishesList(params?: { channel?: string; page?: number; page_size?: number; status?: string }): Promise<Models.PaginatedPublishList>;

  /**
   * Get recent publishes
   * 
   * Returns a paginated list of recent Centrifugo publishes with their
   * details. Uses standard DRF pagination.
   */
  async centrifugoMonitorPublishesList(...args: any[]): Promise<Models.PaginatedPublishList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { channel: args[0], page: args[1], page_size: args[2], status: args[3] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/publishes/", { params });
    return response;
  }

  async centrifugoMonitorTimelineRetrieve(hours?: number, interval?: string): Promise<Models.TimelineResponse>;
  async centrifugoMonitorTimelineRetrieve(params?: { hours?: number; interval?: string }): Promise<Models.TimelineResponse>;

  /**
   * Get publish timeline
   * 
   * Returns hourly or daily breakdown of publish counts for charts.
   */
  async centrifugoMonitorTimelineRetrieve(...args: any[]): Promise<Models.TimelineResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0], interval: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/timeline/", { params });
    return response;
  }

}