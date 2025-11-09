import * as Models from "./models";


/**
 * API endpoints for Centrifugo.
 */
export class CfgCentrifugo {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get statistics per channel.
   */
  async monitorChannelsRetrieve(): Promise<Models.Publish> {
    const response = await this.client.request('GET', "/cfg/centrifugo/monitor/channels/");
    return response;
  }

}