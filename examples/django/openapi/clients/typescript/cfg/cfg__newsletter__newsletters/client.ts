import * as Models from "./models";


/**
 * API endpoints for Newsletters.
 */
export class CfgNewslettersAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List Active Newsletters
 * 
 * Get a list of all active newsletters available for subscription.
 */
async list(page?: number | null, page_size?: number | null): Promise<Models.PaginatedNewsletterList[]> {
  const response = await this.client.request<Models.PaginatedNewsletterList[]>('GET', "/django_cfg_newsletter/newsletters/", { params: { page, page_size } });
  return (response as any).results || [];
}

  /**
 * Get Newsletter Details
 * 
 * Retrieve details of a specific newsletter.
 */
async retrieve(id: number): Promise<Models.Newsletter> {
  const response = await this.client.request<Models.Newsletter>('GET', `/django_cfg_newsletter/newsletters/${id}/`);
  return response;
}

}