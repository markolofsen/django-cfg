import * as Models from "./models";


/**
 * API endpoints for Crypto Client Commands.
 */
export class CryptoClientCommands {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * List active crypto clients
   * 
   * List all active crypto clients.
   */
  async cryptoCommandsRetrieve(): Promise<any> {
    const response = await this.client.request('GET', "/api/crypto/commands/");
    return response;
  }

  /**
   * Get crypto client details
   * 
   * Get specific crypto client details.
   */
  async cryptoCommandsRetrieve2(id: string): Promise<any> {
    const response = await this.client.request('GET', `/api/crypto/commands/${id}/`);
    return response;
  }

  /**
   * Pause crypto client
   * 
   * Pause crypto client and send PAUSE command via gRPC streaming
   * (synchronous).
   */
  async cryptoCommandsPauseCreate(id: string): Promise<Models.ClientCommand> {
    const response = await this.client.request('POST', `/api/crypto/commands/${id}/pause/`);
    return response;
  }

  /**
   * Ping crypto client
   * 
   * Send PING command to crypto client via gRPC streaming (synchronous).
   */
  async cryptoCommandsPingCreate(id: string): Promise<any> {
    const response = await this.client.request('POST', `/api/crypto/commands/${id}/ping/`);
    return response;
  }

  async cryptoCommandsRequestStatusCreate(id: string, include_stats?: boolean): Promise<Models.ClientCommand>;
  async cryptoCommandsRequestStatusCreate(id: string, params?: { include_stats?: boolean }): Promise<Models.ClientCommand>;

  /**
   * Request status from crypto client
   * 
   * Request status from crypto client via gRPC streaming (synchronous).
   */
  async cryptoCommandsRequestStatusCreate(...args: any[]): Promise<Models.ClientCommand> {
    const id = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { include_stats: args[1] };
    }
    const response = await this.client.request('POST', `/api/crypto/commands/${id}/request_status/`, { params });
    return response;
  }

  /**
   * Resume crypto client
   * 
   * Resume paused crypto client and send RESUME command via gRPC streaming
   * (synchronous).
   */
  async cryptoCommandsResumeCreate(id: string): Promise<Models.ClientCommand> {
    const response = await this.client.request('POST', `/api/crypto/commands/${id}/resume/`);
    return response;
  }

  async cryptoCommandsSyncWalletsCreate(id: string, symbols?: string): Promise<any>;
  async cryptoCommandsSyncWalletsCreate(id: string, params?: { symbols?: string }): Promise<any>;

  /**
   * Sync wallets on crypto client
   * 
   * Request wallet sync from crypto client via gRPC streaming (synchronous).
   */
  async cryptoCommandsSyncWalletsCreate(...args: any[]): Promise<any> {
    const id = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { symbols: args[1] };
    }
    const response = await this.client.request('POST', `/api/crypto/commands/${id}/sync_wallets/`, { params });
    return response;
  }

  /**
   * Pause all crypto clients
   * 
   * Pause all active crypto clients.
   */
  async cryptoCommandsPauseAllCreate(): Promise<any> {
    const response = await this.client.request('POST', "/api/crypto/commands/pause_all/");
    return response;
  }

  /**
   * Resume all crypto clients
   * 
   * Resume all active crypto clients.
   */
  async cryptoCommandsResumeAllCreate(): Promise<any> {
    const response = await this.client.request('POST', "/api/crypto/commands/resume_all/");
    return response;
  }

  async cryptoCommandsSyncAllCreate(symbols?: string): Promise<any>;
  async cryptoCommandsSyncAllCreate(params?: { symbols?: string }): Promise<any>;

  /**
   * Sync wallets on all crypto clients
   * 
   * Trigger wallet sync on all active crypto clients.
   */
  async cryptoCommandsSyncAllCreate(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { symbols: args[0] };
    }
    const response = await this.client.request('POST', "/api/crypto/commands/sync_all/", { params });
    return response;
  }

}