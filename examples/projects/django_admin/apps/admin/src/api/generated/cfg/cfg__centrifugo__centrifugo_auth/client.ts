import * as Models from "./models";


/**
 * API endpoints for Centrifugo Auth.
 */
export class CfgCentrifugoAuth {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get Centrifugo connection token
   * 
   * Generate JWT token for WebSocket connection to Centrifugo. Token
   * includes user's allowed channels based on their permissions. Requires
   * authentication.
   */
  async tokenRetrieve(): Promise<Models.ConnectionTokenResponse> {
    const response = await this.client.request('GET', "/cfg/centrifugo/auth/token/");
    return response;
  }

}