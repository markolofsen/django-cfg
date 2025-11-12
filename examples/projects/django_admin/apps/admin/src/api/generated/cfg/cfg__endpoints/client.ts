import * as Models from "./models";


/**
 * API endpoints for Endpoints.
 */
export class CfgEndpoints {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Return endpoints status data.
   */
  async drfRetrieve(): Promise<Models.EndpointsStatus> {
    const response = await this.client.request('GET', "/cfg/endpoints/drf/");
    return response;
  }

  /**
   * Return all registered URLs.
   */
  async urlsRetrieve(): Promise<Models.URLsList[]> {
    const response = await this.client.request('GET', "/cfg/endpoints/urls/");
    return (response as any).results || response;
  }

  /**
   * Return compact URL list.
   */
  async urlsCompactRetrieve(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/endpoints/urls/compact/");
    return response;
  }

}