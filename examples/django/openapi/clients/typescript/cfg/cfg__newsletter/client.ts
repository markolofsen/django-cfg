import * as Models from "./models";


/**
 * API endpoints for Newsletter.
 */
export class CfgNewsletterAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * Retrieve, update, or delete a newsletter campaign.
 */
async campaignsPartialUpdate(id: number, data?: Models.PatchedNewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
  const response = await this.client.request<Models.NewsletterCampaign>('PATCH', `/django_cfg_newsletter/campaigns/${id}/`, { body: data });
  return response;
}

  /**
 * Handle newsletter unsubscriptions.
 */
async unsubscribeUpdate(data: Models.UnsubscribeRequest): Promise<Models.Unsubscribe> {
  const response = await this.client.request<Models.Unsubscribe>('PUT', "/django_cfg_newsletter/unsubscribe/", { body: data });
  return response;
}

  /**
 * Handle newsletter unsubscriptions.
 */
async unsubscribePartialUpdate(data?: Models.PatchedUnsubscribeRequest): Promise<Models.Unsubscribe> {
  const response = await this.client.request<Models.Unsubscribe>('PATCH', "/django_cfg_newsletter/unsubscribe/", { body: data });
  return response;
}

}