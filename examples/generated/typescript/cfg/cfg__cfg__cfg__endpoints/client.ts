import * as Models from "./models";


/**
 * API endpoints for Cfg Endpoints.
 */
export class CfgEndpointsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Return endpoints status data.
   */
  async cfgEndpointsDrfRetrieve(): Promise<Models.EndpointsStatus> {
    const response = await this.client.request('GET', "/cfg/endpoints/drf/");
    return response;
  }

}