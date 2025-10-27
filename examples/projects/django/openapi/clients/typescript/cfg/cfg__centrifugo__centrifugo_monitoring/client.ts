import * as Models from "./models";


/**
 * API endpoints for Centrifugo Monitoring.
 */
export class CfgCentrifugoMonitoring {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get Centrifugo health status
   * 
   * Returns the current health status of the Centrifugo client.
   */
  async centrifugoAdminApiMonitorHealthRetrieve(): Promise<Models.HealthCheck> {
    const response = await this.client.request('GET', "/cfg/centrifugo/admin/api/monitor/health/");
    return response;
  }

  async centrifugoAdminApiMonitorOverviewRetrieve(hours?: number): Promise<Models.OverviewStats>;
  async centrifugoAdminApiMonitorOverviewRetrieve(params?: { hours?: number }): Promise<Models.OverviewStats>;

  /**
   * Get overview statistics
   * 
   * Returns overview statistics for Centrifugo publishes.
   */
  async centrifugoAdminApiMonitorOverviewRetrieve(...args: any[]): Promise<Models.OverviewStats> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/admin/api/monitor/overview/", { params });
    return response;
  }

  async centrifugoAdminApiMonitorPublishesRetrieve(channel?: string, count?: number, offset?: number, status?: string): Promise<Models.RecentPublishes>;
  async centrifugoAdminApiMonitorPublishesRetrieve(params?: { channel?: string; count?: number; offset?: number; status?: string }): Promise<Models.RecentPublishes>;

  /**
   * Get recent publishes
   * 
   * Returns a list of recent Centrifugo publishes with their details.
   */
  async centrifugoAdminApiMonitorPublishesRetrieve(...args: any[]): Promise<Models.RecentPublishes> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { channel: args[0], count: args[1], offset: args[2], status: args[3] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/admin/api/monitor/publishes/", { params });
    return response;
  }

  async centrifugoAdminApiMonitorTimelineRetrieve(hours?: number, interval?: string): Promise<Models.ChannelList[]>;
  async centrifugoAdminApiMonitorTimelineRetrieve(params?: { hours?: number; interval?: string }): Promise<Models.ChannelList[]>;

  /**
   * Get channel statistics
   * 
   * Returns statistics grouped by channel.
   */
  async centrifugoAdminApiMonitorTimelineRetrieve(...args: any[]): Promise<Models.ChannelList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0], interval: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/admin/api/monitor/timeline/", { params });
    return (response as any).results || [];
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

  async centrifugoMonitorOverviewRetrieve(hours?: number): Promise<Models.OverviewStats>;
  async centrifugoMonitorOverviewRetrieve(params?: { hours?: number }): Promise<Models.OverviewStats>;

  /**
   * Get overview statistics
   * 
   * Returns overview statistics for Centrifugo publishes.
   */
  async centrifugoMonitorOverviewRetrieve(...args: any[]): Promise<Models.OverviewStats> {
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

  async centrifugoMonitorPublishesRetrieve(channel?: string, count?: number, offset?: number, status?: string): Promise<Models.RecentPublishes>;
  async centrifugoMonitorPublishesRetrieve(params?: { channel?: string; count?: number; offset?: number; status?: string }): Promise<Models.RecentPublishes>;

  /**
   * Get recent publishes
   * 
   * Returns a list of recent Centrifugo publishes with their details.
   */
  async centrifugoMonitorPublishesRetrieve(...args: any[]): Promise<Models.RecentPublishes> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { channel: args[0], count: args[1], offset: args[2], status: args[3] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/publishes/", { params });
    return response;
  }

  async centrifugoMonitorTimelineRetrieve(hours?: number, interval?: string): Promise<Models.ChannelList[]>;
  async centrifugoMonitorTimelineRetrieve(params?: { hours?: number; interval?: string }): Promise<Models.ChannelList[]>;

  /**
   * Get channel statistics
   * 
   * Returns statistics grouped by channel.
   */
  async centrifugoMonitorTimelineRetrieve(...args: any[]): Promise<Models.ChannelList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0], interval: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/timeline/", { params });
    return (response as any).results || [];
  }

}