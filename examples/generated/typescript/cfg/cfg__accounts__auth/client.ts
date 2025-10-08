import * as Models from "./models";


/**
 * API endpoints for Auth.
 */
export class CfgAuthAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Refresh JWT token.
   */
  async tokenRefreshCreate(data: Models.TokenRefreshRequest): Promise<Models.TokenRefresh> {
    const response = await this.client.request('POST', "/django_cfg_accounts/token/refresh/", { body: data });
    return response;
  }

}