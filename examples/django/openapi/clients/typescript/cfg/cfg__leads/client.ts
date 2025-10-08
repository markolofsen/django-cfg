import * as Models from "./models";


/**
 * API endpoints for Leads.
 */
export class CfgLeadsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * ViewSet for Lead model. Provides only submission functionality for leads
 * from frontend forms.
 */
async list(page?: number | null, page_size?: number | null): Promise<Models.PaginatedLeadSubmissionList[]> {
  const response = await this.client.request<Models.PaginatedLeadSubmissionList[]>('GET', "/django_cfg_leads/leads/", { params: { page, page_size } });
  return (response as any).results || [];
}

  /**
 * ViewSet for Lead model. Provides only submission functionality for leads
 * from frontend forms.
 */
async create(data: Models.LeadSubmissionRequest): Promise<Models.LeadSubmission> {
  const response = await this.client.request<Models.LeadSubmission>('POST', "/django_cfg_leads/leads/", { body: data });
  return response;
}

  /**
 * ViewSet for Lead model. Provides only submission functionality for leads
 * from frontend forms.
 */
async retrieve(id: number): Promise<Models.LeadSubmission> {
  const response = await this.client.request<Models.LeadSubmission>('GET', `/django_cfg_leads/leads/${id}/`);
  return response;
}

  /**
 * ViewSet for Lead model. Provides only submission functionality for leads
 * from frontend forms.
 */
async update(id: number, data: Models.LeadSubmissionRequest): Promise<Models.LeadSubmission> {
  const response = await this.client.request<Models.LeadSubmission>('PUT', `/django_cfg_leads/leads/${id}/`, { body: data });
  return response;
}

  /**
 * ViewSet for Lead model. Provides only submission functionality for leads
 * from frontend forms.
 */
async partialUpdate(id: number, data?: Models.PatchedLeadSubmissionRequest): Promise<Models.LeadSubmission> {
  const response = await this.client.request<Models.LeadSubmission>('PATCH', `/django_cfg_leads/leads/${id}/`, { body: data });
  return response;
}

  /**
 * ViewSet for Lead model. Provides only submission functionality for leads
 * from frontend forms.
 */
async destroy(id: number): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/django_cfg_leads/leads/${id}/`);
  return;
}

}