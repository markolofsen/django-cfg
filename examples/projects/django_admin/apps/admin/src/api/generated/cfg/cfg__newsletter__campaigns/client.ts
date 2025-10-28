import * as Models from "./models";


/**
 * API endpoints for Campaigns.
 */
export class CfgCampaigns {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async newsletterCampaignsList(page?: number, page_size?: number): Promise<Models.PaginatedNewsletterCampaignList>;
  async newsletterCampaignsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedNewsletterCampaignList>;

  /**
   * List Newsletter Campaigns
   * 
   * Get a list of all newsletter campaigns.
   */
  async newsletterCampaignsList(...args: any[]): Promise<Models.PaginatedNewsletterCampaignList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/newsletter/campaigns/", { params });
    return response;
  }

  /**
   * Create Newsletter Campaign
   * 
   * Create a new newsletter campaign.
   */
  async newsletterCampaignsCreate(data: Models.NewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
    const response = await this.client.request('POST', "/cfg/newsletter/campaigns/", { body: data });
    return response;
  }

  /**
   * Get Campaign Details
   * 
   * Retrieve details of a specific newsletter campaign.
   */
  async newsletterCampaignsRetrieve(id: number): Promise<Models.NewsletterCampaign> {
    const response = await this.client.request('GET', `/cfg/newsletter/campaigns/${id}/`);
    return response;
  }

  /**
   * Update Campaign
   * 
   * Update a newsletter campaign.
   */
  async newsletterCampaignsUpdate(id: number, data: Models.NewsletterCampaignRequest): Promise<Models.NewsletterCampaign> {
    const response = await this.client.request('PUT', `/cfg/newsletter/campaigns/${id}/`, { body: data });
    return response;
  }

  /**
   * Delete Campaign
   * 
   * Delete a newsletter campaign.
   */
  async newsletterCampaignsDestroy(id: number): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/newsletter/campaigns/${id}/`);
    return;
  }

  /**
   * Send Newsletter Campaign
   * 
   * Send a newsletter campaign to all subscribers.
   */
  async newsletterCampaignsSendCreate(data: Models.SendCampaignRequest): Promise<Models.SendCampaignResponse> {
    const response = await this.client.request('POST', "/cfg/newsletter/campaigns/send/", { body: data });
    return response;
  }

}