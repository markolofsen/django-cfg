import * as Models from "./models";


/**
 * API endpoints for Auth.
 */
export class CfgAuth {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Refresh JWT token.
   */
  async accountsTokenRefreshCreate(data: Models.TokenRefreshRequest): Promise<Models.TokenRefresh> {
    const response = await this.client.request('POST', "/cfg/accounts/token/refresh/", { body: data });
    return response;
  }

}