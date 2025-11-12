import * as Models from "./models";


/**
 * API endpoints for Centrifugo Admin API.
 */
export class CfgCentrifugoAdminApi {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get connection token for dashboard
   * 
   * Returns JWT token and config for WebSocket connection to Centrifugo.
   */
  async centrifugoServerAuthTokenCreate(): Promise<any> {
    const response = await this.client.request('POST', "/cfg/centrifugo/server/auth/token/");
    return response;
  }

  /**
   * List active channels
   * 
   * Returns list of active channels with optional pattern filter.
   */
  async centrifugoServerChannelsCreate(data: Models.CentrifugoChannelsRequestRequest): Promise<Models.CentrifugoChannelsResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/server/channels/", { body: data });
    return response;
  }

  /**
   * Get channel history
   * 
   * Returns message history for a channel.
   */
  async centrifugoServerHistoryCreate(data: Models.CentrifugoHistoryRequestRequest): Promise<Models.CentrifugoHistoryResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/server/history/", { body: data });
    return response;
  }

  /**
   * Get Centrifugo server info
   * 
   * Returns server information including node count, version, and uptime.
   */
  async centrifugoServerInfoCreate(): Promise<Models.CentrifugoInfoResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/server/info/");
    return response;
  }

  /**
   * Get channel presence
   * 
   * Returns list of clients currently subscribed to a channel.
   */
  async centrifugoServerPresenceCreate(data: Models.CentrifugoPresenceRequestRequest): Promise<Models.CentrifugoPresenceResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/server/presence/", { body: data });
    return response;
  }

  /**
   * Get channel presence statistics
   * 
   * Returns quick statistics about channel presence (num_clients,
   * num_users).
   */
  async centrifugoServerPresenceStatsCreate(data: Models.CentrifugoPresenceStatsRequestRequest): Promise<Models.CentrifugoPresenceStatsResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/server/presence-stats/", { body: data });
    return response;
  }

}