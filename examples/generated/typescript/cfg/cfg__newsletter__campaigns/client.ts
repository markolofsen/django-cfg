import * as Models from "./models";


/**
 * API endpoints for Campaigns.
 */
export class CfgCampaignsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(page?: number, page_size?: number): Promise<Models.PaginatedNewsletterCampaignList[]>;
  async list(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedNewsletterCampaignList[]>;

  /**
   * List Newsletter Campaigns
   * 
   * Get a list of all newsletter campaigns.
   */
  async list(...args: any[]): Promise<Models.PaginatedNewsletterCampaignList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/django_cfg_newsletter/campaigns/", { params });
    return (response as any).results || [];
  }

  /**
   * Create Newsletter Campaign
   * 
   * Create a new newsletter campaign.
   */
  async create(data: Models.NewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
    const response = await this.client.request('POST', "/django_cfg_newsletter/campaigns/", { body: data });
    return response;
  }

  /**
   * Get Campaign Details
   * 
   * Retrieve details of a specific newsletter campaign.
   */
  async retrieve(id: number): Promise<Models.NewsletterCampaign> {
    const response = await this.client.request('GET', `/django_cfg_newsletter/campaigns/${id}/`);
    return response;
  }

  /**
   * Update Campaign
   * 
   * Update a newsletter campaign.
   */
  async update(id: number, data: Models.NewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
    const response = await this.client.request('PUT', `/django_cfg_newsletter/campaigns/${id}/`, { body: data });
    return response;
  }

  /**
   * Delete Campaign
   * 
   * Delete a newsletter campaign.
   */
  async destroy(id: number): Promise<void> {
    const response = await this.client.request('DELETE', `/django_cfg_newsletter/campaigns/${id}/`);
    return;
  }

  /**
   * Send Newsletter Campaign
   * 
   * Send a newsletter campaign to all subscribers.
   */
  async sendCreate(data: Models.SendCampaignRequest): Promise<Models.SendCampaignResponse> {
    const response = await this.client.request('POST', "/django_cfg_newsletter/campaigns/send/", { body: data });
    return response;
  }

}