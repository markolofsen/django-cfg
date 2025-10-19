import * as Models from "./models";


/**
 * API endpoints for Lead Submission.
 */
export class CfgLeadSubmission {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Submit Lead Form
   * 
   * Submit a new lead from frontend contact form with automatic Telegram
   * notifications.
   */
  async leadsSubmitCreate(data: Models.LeadSubmissionRequest): Promise<Models.LeadSubmissionResponse> {
    const response = await this.client.request('POST', "/cfg/leads/submit/", { body: data });
    return response;
  }

}