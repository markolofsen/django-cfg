import * as Models from "./models";


/**
 * API endpoints for Campaigns.
 */
export class CfgCampaignsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List Newsletter Campaigns
 * 
 * Get a list of all newsletter campaigns.
 */
async list(page?: number | null, page_size?: number | null): Promise<Models.PaginatedNewsletterCampaignList[]> {
  const response = await this.client.request<Models.PaginatedNewsletterCampaignList[]>('GET', "/django_cfg_newsletter/campaigns/", { params: { page, page_size } });
  return (response as any).results || [];
}

  /**
 * Create Newsletter Campaign
 * 
 * Create a new newsletter campaign.
 */
async create(data: Models.NewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
  const response = await this.client.request<Models.NewsletterCampaign>('POST', "/django_cfg_newsletter/campaigns/", { body: data });
  return response;
}

  /**
 * Get Campaign Details
 * 
 * Retrieve details of a specific newsletter campaign.
 */
async retrieve(id: number): Promise<Models.NewsletterCampaign> {
  const response = await this.client.request<Models.NewsletterCampaign>('GET', `/django_cfg_newsletter/campaigns/${id}/`);
  return response;
}

  /**
 * Update Campaign
 * 
 * Update a newsletter campaign.
 */
async update(id: number, data: Models.NewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
  const response = await this.client.request<Models.NewsletterCampaign>('PUT', `/django_cfg_newsletter/campaigns/${id}/`, { body: data });
  return response;
}

  /**
 * Delete Campaign
 * 
 * Delete a newsletter campaign.
 */
async destroy(id: number): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/django_cfg_newsletter/campaigns/${id}/`);
  return;
}

  /**
 * Send Newsletter Campaign
 * 
 * Send a newsletter campaign to all subscribers.
 */
async sendCreate(data: Models.SendCampaignRequest): Promise<Models.SendCampaignResponse> {
  const response = await this.client.request<Models.SendCampaignResponse>('POST', "/django_cfg_newsletter/campaigns/send/", { body: data });
  return response;
}

}