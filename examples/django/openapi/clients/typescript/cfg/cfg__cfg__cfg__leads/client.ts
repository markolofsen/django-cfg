import * as Models from "./models";


/**
 * API endpoints for Cfg Leads.
 */
export class CfgLeadsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async cfgLeadsLeadsList(page?: number, page_size?: number): Promise<Models.PaginatedLeadSubmissionList[]>;
  async cfgLeadsLeadsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedLeadSubmissionList[]>;

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async cfgLeadsLeadsList(...args: any[]): Promise<Models.PaginatedLeadSubmissionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/leads/leads/", { params });
    return (response as any).results || [];
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async cfgLeadsLeadsCreate(data: Models.LeadSubmissionRequest): Promise<Models.LeadSubmission> {
    const response = await this.client.request('POST', "/cfg/leads/leads/", { body: data });
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async cfgLeadsLeadsRetrieve(id: number): Promise<Models.LeadSubmission> {
    const response = await this.client.request('GET', `/cfg/leads/leads/${id}/`);
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async cfgLeadsLeadsUpdate(id: number, data: Models.LeadSubmissionRequest): Promise<Models.LeadSubmission> {
    const response = await this.client.request('PUT', `/cfg/leads/leads/${id}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async cfgLeadsLeadsPartialUpdate(id: number, data?: Models.PatchedLeadSubmissionRequest): Promise<Models.LeadSubmission> {
    const response = await this.client.request('PATCH', `/cfg/leads/leads/${id}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for Lead model. Provides only submission functionality for leads
   * from frontend forms.
   */
  async cfgLeadsLeadsDestroy(id: number): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/leads/leads/${id}/`);
    return;
  }

}