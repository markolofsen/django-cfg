import * as Models from "./models";


/**
 * API endpoints for Newsletter.
 */
export class CfgNewsletter {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Retrieve, update, or delete a newsletter campaign.
   */
  async campaignsPartialUpdate(id: number, data?: Models.PatchedNewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
    const response = await this.client.request('PATCH', `/cfg/newsletter/campaigns/${id}/`, { body: data });
    return response;
  }

  /**
   * Handle newsletter unsubscriptions.
   */
  async unsubscribeUpdate(data: Models.UnsubscribeRequest): Promise<Models.Unsubscribe> {
    const response = await this.client.request('PUT', "/cfg/newsletter/unsubscribe/", { body: data });
    return response;
  }

  /**
   * Handle newsletter unsubscriptions.
   */
  async unsubscribePartialUpdate(data?: Models.PatchedUnsubscribeRequest): Promise<Models.Unsubscribe> {
    const response = await this.client.request('PATCH', "/cfg/newsletter/unsubscribe/", { body: data });
    return response;
  }

}