import * as Models from "./models";


/**
 * API endpoints for Grpc Api Keys.
 */
export class CfgGrpcApiKeys {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(is_active?: boolean, key_type?: string, page?: number, page_size?: number, user_id?: number): Promise<Models.PaginatedApiKeyList>;
  async list(params?: { is_active?: boolean; key_type?: string; page?: number; page_size?: number; user_id?: number }): Promise<Models.PaginatedApiKeyList>;

  /**
   * List API keys
   * 
   * Returns a list of all API keys with their details. Uses standard DRF
   * pagination.
   */
  async list(...args: any[]): Promise<Models.PaginatedApiKeyList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { is_active: args[0], key_type: args[1], page: args[2], page_size: args[3], user_id: args[4] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/api-keys/", { params });
    return response;
  }

  /**
   * Get API key details
   * 
   * Returns detailed information about a specific API key.
   */
  async retrieve(id: number): Promise<Models.ApiKey> {
    const response = await this.client.request('GET', `/cfg/grpc/api-keys/${id}/`);
    return response;
  }

  /**
   * Get API keys statistics
   * 
   * Returns overall statistics about API keys usage.
   */
  async statsRetrieve(): Promise<Models.ApiKeyStats> {
    const response = await this.client.request('GET', "/cfg/grpc/api-keys/stats/");
    return response;
  }

}