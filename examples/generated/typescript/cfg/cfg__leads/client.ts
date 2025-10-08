import * as Models from "./models";


/**
 * API endpoints for Leads.
 */
export class CfgLeadsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(page?: number, page_size?: number): Promise<Models.PaginatedLeadSubmissionList[]>;
  async list(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedLeadSubmissionList[]>;

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async list(...args: any[]): Promise<Models.PaginatedLeadSubmissionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/django_cfg_leads/leads/", { params });
    return (response as any).results || [];
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async create(data: Models.LeadSubmissionRequest): Promise<Models.LeadSubmission> {
    const response = await this.client.request('POST', "/django_cfg_leads/leads/", { body: data });
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async retrieve(id: number): Promise<Models.LeadSubmission> {
    const response = await this.client.request('GET', `/django_cfg_leads/leads/${id}/`);
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async update(id: number, data: Models.LeadSubmissionRequest): Promise<Models.LeadSubmission> {
    const response = await this.client.request('PUT', `/django_cfg_leads/leads/${id}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async partialUpdate(id: number, data?: Models.PatchedLeadSubmissionRequest): Promise<Models.LeadSubmission> {
    const response = await this.client.request('PATCH', `/django_cfg_leads/leads/${id}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async destroy(id: number): Promise<void> {
    const response = await this.client.request('DELETE', `/django_cfg_leads/leads/${id}/`);
    return;
  }

}