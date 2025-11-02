import * as Models from "./models";


/**
 * API endpoints for Newsletters.
 */
export class CfgNewsletters {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async newsletterNewslettersList(page?: number, page_size?: number): Promise<Models.PaginatedNewsletterList>;
  async newsletterNewslettersList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedNewsletterList>;

  /**
   * List Active Newsletters
   * 
   * Get a list of all active newsletters available for subscription.
   */
  async newsletterNewslettersList(...args: any[]): Promise<Models.PaginatedNewsletterList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/newsletter/newsletters/", { params });
    return response;
  }

  /**
   * Get Newsletter Details
   * 
   * Retrieve details of a specific newsletter.
   */
  async newsletterNewslettersRetrieve(id: number): Promise<Models.Newsletter> {
    const response = await this.client.request('GET', `/cfg/newsletter/newsletters/${id}/`);
    return response;
  }

}