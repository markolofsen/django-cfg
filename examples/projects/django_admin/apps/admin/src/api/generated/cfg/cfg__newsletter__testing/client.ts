import * as Models from "./models";


/**
 * API endpoints for Testing.
 */
export class CfgTesting {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Test Email Sending
   * 
   * Send a test email to verify mailer configuration.
   */
  async newsletterTestCreate(data: Models.TestEmailRequest): Promise<Models.BulkEmailResponse> {
    const response = await this.client.request('POST', "/cfg/newsletter/test/", { body: data });
    return response;
  }

}